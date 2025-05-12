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
        // First, get user info to display name
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
            // Leer descripción desde localStorage (vulnerabilidad DOM XSS)
            let unsafeName = localStorage.getItem('xss_name');
            if (!unsafeName) unsafeName = project.name;
            projectItem.querySelector('.project-name').innerHTML = unsafeName;

            projectItem.querySelector('.project-uuid').textContent = `UUID: ${project.uuid}`;
            projectItem.querySelector('.project-description').innerHTML = `Descripción: ${project.description}`;
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
    projectModal.show();
}

async function saveProject() {
    const name = projectNameInput.value.trim();
    if (!name) {
        alert('El nombre del proyecto es obligatorio');
        return;
    }

    const description = projectDescriptionInput.value.trim();
    const uuid = projectUuidInput.value;

    try {
        const response = await fetch(`/sql/projects/${uuid}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const updatedProject = await response.json();
        projectModal.hide();

        // Reload the projects list
        loadUserProjects();
        createAlert(`Proyecto actualizado con éxito.`, 'success');

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

document.addEventListener('DOMContentLoaded', loadUserProjects);