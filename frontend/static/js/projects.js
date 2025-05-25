const projectsList = document.getElementById('projects-list');
const nameDisplay = document.getElementById('name-display');
const breadcrumbname = document.getElementById('breadcrumb-name');
const notificationArea = document.getElementById('notification-area');

const alertTemplate = document.getElementById('alert-template');
const loadingTemplate = document.getElementById('loading-template');
const emptyProjectsTemplate = document.getElementById('empty-projects-template');
const errorTemplate = document.getElementById('error-template');
const projectItemTemplate = document.getElementById('project-item-template');
const projectsContainerTemplate = document.getElementById('projects-container-template');

const projectModal = new bootstrap.Modal(document.getElementById('projectModal'));
const projectForm = document.getElementById('projectForm');
const projectUuidInput = document.getElementById('projectUuid');
const projectNameInput = document.getElementById('projectName');
const projectDescriptionInput = document.getElementById('projectDescription');
const saveProjectBtn = document.getElementById('saveProjectBtn');
const projectModalLabel = document.getElementById('projectModalLabel');

const vulnerabilityDropdown = document.getElementById('vulnerabilityDropdown');
const selectedVulnerabilityInput = document.getElementById('selectedVulnerability');
const customVulnerabilityInput = document.getElementById('customVulnerability');

const totalVulnerabilitiesInput = document.getElementById('totalVulnerabilities');
const solvabilityDropdown = document.getElementById('solvabilityDropdown');
const selectedSolvabilityInput = document.getElementById('selectedSolvability');

const fileUploadSection = document.getElementById('fileUploadSection');

function initializeDropdown() {
    // Initialize vulnerability dropdown
    if (vulnerabilityDropdown) {
        const vulnerabilityDropdownContent = document.querySelector('#vulnerabilityLevelSection .dropdown-content');
        if (!vulnerabilityDropdownContent) return;
        
        const vulnerabilityDropdownOptions = vulnerabilityDropdownContent.querySelectorAll('a[data-value]');
        const customVulnerabilityContainer = document.getElementById('customVulnerabilityContainer');
        const vulnerabilityDropdownContainer = document.querySelector('#vulnerabilityLevelSection .dropdown');
        
        vulnerabilityDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (vulnerabilityDropdownContainer) {
                vulnerabilityDropdownContainer.classList.toggle('show');
            }
        });
        
        vulnerabilityDropdownOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const value = this.getAttribute('data-value');
                const text = this.textContent.trim();
                
                vulnerabilityDropdown.textContent = text;
                
                if (value === 'custom') {
                    if (customVulnerabilityContainer) {
                        customVulnerabilityContainer.style.display = 'block';
                    }
                    selectedVulnerabilityInput.value = '';
                    if (customVulnerabilityInput) {
                        customVulnerabilityInput.value = '';
                        customVulnerabilityInput.focus();
                    }
                } else {
                    if (customVulnerabilityContainer) {
                        customVulnerabilityContainer.style.display = 'none';
                    }
                    selectedVulnerabilityInput.value = value;
                    if (customVulnerabilityInput) {
                        customVulnerabilityInput.value = '';
                    }
                }
                
                if (vulnerabilityDropdownContainer) {
                    vulnerabilityDropdownContainer.classList.remove('show');
                }
            });
        });
        
        if (customVulnerabilityInput) {
            customVulnerabilityInput.addEventListener('input', function() {
                if (this.value.trim()) {
                    selectedVulnerabilityInput.value = this.value.trim();
                } else {
                    selectedVulnerabilityInput.value = '';
                }
            });
        }
    }
    
    // Initialize solvability dropdown
    if (solvabilityDropdown) {
        const solvabilityDropdownContent = document.querySelector('#solvabilityCriteriaSection .dropdown-content');
        if (!solvabilityDropdownContent) return;
        
        const solvabilityDropdownOptions = solvabilityDropdownContent.querySelectorAll('a[data-value]');
        const solvabilityDropdownContainer = document.querySelector('#solvabilityCriteriaSection .dropdown');
        
        solvabilityDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (solvabilityDropdownContainer) {
                solvabilityDropdownContainer.classList.toggle('show');
            }
        });
        
        solvabilityDropdownOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const value = this.getAttribute('data-value');
                const text = this.textContent.trim();
                
                solvabilityDropdown.textContent = text;
                selectedSolvabilityInput.value = value;
                
                if (solvabilityDropdownContainer) {
                    solvabilityDropdownContainer.classList.remove('show');
                }
            });
        });
    }
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });
}

function createAlert(message, category = 'danger') {
    const alertNode = alertTemplate.content.cloneNode(true);
    const alertDiv = alertNode.querySelector('.alert');

    alertDiv.classList.add(`alert-${category}`);
    alertDiv.querySelector('.alert-message').textContent = message;

    notificationArea.insertBefore(alertDiv, notificationArea.firstChild);

    setTimeout(() => {
        if (alertDiv.parentElement) {
            const alertInstance = bootstrap.Alert.getOrCreateInstance(alertDiv);
            if (alertInstance) {
                alertInstance.close();
            }
        }
    }, 5000);
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

async function loadUserProjects() {
    try {
        const userResponse = await fetch(`/sql/users/all`);
        if (!userResponse.ok) {
            throw new Error(`HTTP error! status: ${userResponse.status}`);
        }
        const users = await userResponse.json();
        const user = users.find(u => u.id === userId);

        if (user) {
            nameDisplay.textContent = user.name;
            breadcrumbname.textContent = user.name;
            document.title = `SVAIA - Proyectos de ${user.name}`;
        }

        // Now get the user's projects
        const projectsResponse = await fetch(`/sql/projects/user/${userId}`);
        if (!projectsResponse.ok) {
            throw new Error(`HTTP error! status: ${projectsResponse.status}`);
        }
        const projects = await projectsResponse.json();

        projectsList.innerHTML = '';

        if (projects.length === 0) {
            projectsList.appendChild(emptyProjectsTemplate.content.cloneNode(true));
            return;
        }

        // Create the list container
        const projectsContainer = projectsContainerTemplate.content.cloneNode(true);
        const listGroup = projectsContainer.querySelector('.list-group');

        projects.forEach(project => {
            const projectNode = projectItemTemplate.content.cloneNode(true);
            const projectItem = projectNode.querySelector('.list-group-item');

            // Set data
            projectItem.querySelector('.project-name').textContent = project.name;
            projectItem.querySelector('.project-uuid').textContent = `UUID: ${project.uuid}`;
            projectItem.querySelector('.project-description').textContent = `Descripción: ${project.description}`;
            projectItem.querySelector('.project-created').textContent = `Creado: ${formatDateTime(project.created_at)}`;
            projectItem.querySelector('.project-updated').textContent = `Última modificación: ${formatDateTime(project.updated_at)}`;

            // Set up buttons
            const viewBtn = projectItem.querySelector('.view-messages-btn');
            viewBtn.href = `/admin/project-messages/${project.uuid}`;

            const editBtn = projectItem.querySelector('.edit-btn');
            editBtn.setAttribute('data-project-uuid', project.uuid);
            editBtn.addEventListener('click', () => {
                showEditProjectModal(project);
            });

            const deleteBtn = projectItem.querySelector('.delete-btn');
            deleteBtn.setAttribute('data-project-uuid', project.uuid);
            deleteBtn.addEventListener('click', () => {
                deleteProject(project.uuid, deleteBtn);
            });

            listGroup.appendChild(projectItem);
        });

        projectsList.appendChild(projectsContainer);

    } catch (error) {
        console.error('Error:', error);
        projectsList.innerHTML = '';
        projectsList.appendChild(errorTemplate.content.cloneNode(true));
        createAlert(`Error al cargar proyectos: ${error.message}`);
    }
}

function showEditProjectModal(project) {
    projectModalLabel.textContent = 'Editar Proyecto';
    projectUuidInput.value = project.uuid;
    projectNameInput.value = project.name;
    projectDescriptionInput.value = project.description || '';
    
    // Load existing vulnerability level
    const existingVulnerability = project.max_vulnerability_level || '';
    if (existingVulnerability && vulnerabilityDropdown) {
        const predefinedValues = {
            'critical': 'Grado de vulnerabilidad crítico (8-10)',
            'severe': 'Grado de vulnerabilidad severa (6-7)',
            'mild': 'Grado de vulnerabilidad leve o medio (1-5)'
        };
        
        if (predefinedValues[existingVulnerability]) {
            vulnerabilityDropdown.textContent = predefinedValues[existingVulnerability];
            selectedVulnerabilityInput.value = existingVulnerability;
            if (customVulnerabilityInput) {
                customVulnerabilityInput.value = '';
            }
            const customVulnerabilityContainer = document.getElementById('customVulnerabilityContainer');
            if (customVulnerabilityContainer) {
                customVulnerabilityContainer.style.display = 'none';
            }
        } else {
            vulnerabilityDropdown.textContent = 'Otro (especificar)';
            selectedVulnerabilityInput.value = existingVulnerability;
            if (customVulnerabilityInput) {
                customVulnerabilityInput.value = existingVulnerability;
            }
            const customVulnerabilityContainer = document.getElementById('customVulnerabilityContainer');
            if (customVulnerabilityContainer) {
                customVulnerabilityContainer.style.display = 'block';
            }
        }
    } else {
        if (vulnerabilityDropdown) {
            vulnerabilityDropdown.textContent = 'Elegir';
            selectedVulnerabilityInput.value = '';
        }
        if (customVulnerabilityInput) {
            customVulnerabilityInput.value = '';
        }
        const customVulnerabilityContainer = document.getElementById('customVulnerabilityContainer');
        if (customVulnerabilityContainer) {
            customVulnerabilityContainer.style.display = 'none';
        }
    }
    
    // Load total vulnerabilities criteria
    if (totalVulnerabilitiesInput) {
        totalVulnerabilitiesInput.value = project.total_vulnerabilities_criteria || '';
    }
    
    // Load solvability criteria
    const existingSolvability = project.solvability_criteria || '';
    if (existingSolvability && solvabilityDropdown) {
        const solvabilityValues = {
            'solvable': 'Solo vulnerabilidades solucionables',
            'non_solvable': 'Permitir vulnerabilidades no solucionables',
            'any': 'Sin restricciones'
        };
        
        if (solvabilityValues[existingSolvability]) {
            solvabilityDropdown.textContent = solvabilityValues[existingSolvability];
            selectedSolvabilityInput.value = existingSolvability;
        } else {
            solvabilityDropdown.textContent = 'Elegir';
            selectedSolvabilityInput.value = '';
        }
    } else {
        if (solvabilityDropdown) {
            solvabilityDropdown.textContent = 'Elegir';
            selectedSolvabilityInput.value = '';
        }
    }
    
    const dockerfilesInput = document.getElementById('dockerfiles');
    const dockerComposeFilesInput = document.getElementById('dockerComposeFiles');
    const dockerImagesInput = document.getElementById('dockerImages');
    
    if (dockerfilesInput) dockerfilesInput.value = '';
    if (dockerComposeFilesInput) dockerComposeFilesInput.value = '';
    if (dockerImagesInput) dockerImagesInput.value = '';
    
    if (fileUploadSection) {
        fileUploadSection.style.display = 'block';
    }
    
    projectModal.show();
}

async function uploadFiles(projectUuid) {
    try {
        const dockerfilesInput = document.getElementById('dockerfiles');
        const dockerComposeFilesInput = document.getElementById('dockerComposeFiles');
        const dockerImagesInput = document.getElementById('dockerImages');
        
        // Upload Dockerfiles
        if (dockerfilesInput && dockerfilesInput.files.length > 0) {
            const dockerfileFormData = new FormData();
            for (let file of dockerfilesInput.files) {
                dockerfileFormData.append('dockerfiles', file);
            }
            
            const dockerfileResponse = await fetch(`/sql/projects/upload/dockerfiles/${projectUuid}`, {
                method: 'POST',
                body: dockerfileFormData
            });
            
            if (!dockerfileResponse.ok) {
                throw new Error('Error al subir Dockerfiles');
            }
        }
        
        // Upload Docker Compose files
        if (dockerComposeFilesInput && dockerComposeFilesInput.files.length > 0) {
            const composeFormData = new FormData();
            for (let file of dockerComposeFilesInput.files) {
                composeFormData.append('docker_compose_files', file);
            }
            
            const composeResponse = await fetch(`/sql/projects/upload/docker-compose-files/${projectUuid}`, {
                method: 'POST',
                body: composeFormData
            });
            
            if (!composeResponse.ok) {
                throw new Error('Error al subir archivos Docker Compose');
            }
        }
        
        // Upload Docker images
        if (dockerImagesInput && dockerImagesInput.files.length > 0) {
            const imagesFormData = new FormData();
            for (let file of dockerImagesInput.files) {
                imagesFormData.append('images', file);
            }
            
            const imagesResponse = await fetch(`/sql/projects/upload/docker-image/${projectUuid}`, {
                method: 'POST',
                body: imagesFormData
            });
            
            if (!imagesResponse.ok) {
                throw new Error('Error al subir imágenes Docker');
            }
        }
        
        return true;
    } catch (error) {
        console.error('Error uploading files:', error);
        throw error;
    }
}

async function saveProject() {
    const name = projectNameInput.value.trim();
    if (!name) {
        alert('El nombre del proyecto es obligatorio');
        return;
    }
    
    const vulnerabilityLevel = selectedVulnerabilityInput ? 
        (selectedVulnerabilityInput.value.trim() || customVulnerabilityInput?.value.trim()) : '';

    const description = projectDescriptionInput.value.trim();
    const uuid = projectUuidInput.value;
    
    // Get the total vulnerabilities value
    const totalVulnerabilities = totalVulnerabilitiesInput && totalVulnerabilitiesInput.value.trim() ? 
        parseInt(totalVulnerabilitiesInput.value.trim()) : null;
    
    // Get the solvability criteria
    const solvabilityCriteria = selectedSolvabilityInput ? selectedSolvabilityInput.value.trim() : '';

    try {
        const requestBody = {
            name: name,
            description: description
        };
        
        // Only include vulnerability level if it's set
        if (vulnerabilityLevel) {
            requestBody.max_vulnerability_level = vulnerabilityLevel;
        }
        
        // Include total vulnerabilities criteria if set
        if (totalVulnerabilities !== null) {
            requestBody.total_vulnerabilities_criteria = totalVulnerabilities;
        }
        
        // Include solvability criteria if set
        if (solvabilityCriteria) {
            requestBody.solvability_criteria = solvabilityCriteria;
        }
        
        const response = await fetch(`/sql/projects/${uuid}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const updatedProject = await response.json();
        
        // Upload files if any are selected
        const dockerfilesInput = document.getElementById('dockerfiles');
        const dockerComposeFilesInput = document.getElementById('dockerComposeFiles');
        const dockerImagesInput = document.getElementById('dockerImages');
        
        const hasFiles = (dockerfilesInput && dockerfilesInput.files.length > 0) || 
                         (dockerComposeFilesInput && dockerComposeFilesInput.files.length > 0) || 
                         (dockerImagesInput && dockerImagesInput.files.length > 0);
        
        if (hasFiles) {
            try {
                await uploadFiles(uuid);
                createAlert('Proyecto y archivos actualizados con éxito.', 'success');
            } catch (uploadError) {
                createAlert('Proyecto actualizado, pero hubo un error al subir algunos archivos: ' + uploadError.message, 'warning');
            }
        } else {
            createAlert('Proyecto actualizado con éxito.', 'success');
        }
        
        projectModal.hide();
        // Reload the projects list
        loadUserProjects();

    } catch (error) {
        console.error('Error updating project:', error);
        createAlert(`Error al actualizar el proyecto: ${error.message}`, 'danger');
    }
}

async function deleteProject(projectUuid, button) {
    if (!confirm('¿Estás seguro de que deseas eliminar este proyecto? Esta acción no se puede deshacer.')) {
        return;
    }

    const originalHtml = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    try {
        const response = await fetch(`/sql/projects/${projectUuid}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const projectItem = button.closest('.list-group-item');
        projectItem.remove();

        if (document.querySelector('.list-group-item') === null) {
            projectsList.innerHTML = '';
            projectsList.appendChild(emptyProjectsTemplate.content.cloneNode(true));
        }
        createAlert(`Proyecto eliminado con éxito.`, 'success');

    } catch (error) {
        console.error('Error deleting project:', error);
        createAlert(`Error al eliminar el proyecto: ${error.message}`, 'danger');
        button.disabled = false;
        button.innerHTML = originalHtml;
    }
}

// Event listeners
saveProjectBtn.addEventListener('click', saveProject);

document.addEventListener('DOMContentLoaded', function() {
    initializeDropdown();
    loadUserProjects();
});