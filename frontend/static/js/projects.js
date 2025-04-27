const projectsList = document.getElementById('projects-list');
const usernameDisplay = document.getElementById('username-display');
const breadcrumbUsername = document.getElementById('breadcrumb-username');
const notificationArea = document.getElementById('notification-area');

const alertTemplate = document.getElementById('alert-template');
const loadingTemplate = document.getElementById('loading-template');
const emptyProjectsTemplate = document.getElementById('empty-projects-template');
const errorTemplate = document.getElementById('error-template');
const projectItemTemplate = document.getElementById('project-item-template');
const projectsContainerTemplate = document.getElementById('projects-container-template');

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

async function loadUserProjects() {
    try {
        // First, get user info to display username
        const userResponse = await fetch(`/sql/users/all`);
        if (!userResponse.ok) {
            throw new Error(`HTTP error! status: ${userResponse.status}`);
        }
        const users = await userResponse.json();
        const user = users.find(u => u.id === userId);

        if (user) {
            usernameDisplay.textContent = user.username;
            breadcrumbUsername.textContent = user.username;
            document.title = `SVAIA - Proyectos de ${user.username}`;
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

            // Set up buttons
            const viewBtn = projectItem.querySelector('.view-messages-btn');
            viewBtn.href = `/admin/project-messages/${project.uuid}`;

            const editBtn = projectItem.querySelector('.edit-btn');
            editBtn.setAttribute('data-project-uuid', project.uuid);
            editBtn.setAttribute('data-project-name', project.name);
            editBtn.addEventListener('click', () => {
                editProject(project.uuid, project.name, editBtn);
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

async function editProject(projectUuid, currentName, button) {
    const newName = prompt("Ingrese el nuevo nombre para el proyecto:", currentName);

    if (!newName || newName.trim() === '' || newName === currentName) {
        return; // Cancel or no change
    }

    const projectItem = button.closest('.list-group-item');
    const projectNameElement = projectItem.querySelector('.project-name');
    const originalName = projectNameElement.textContent;

    // Disable button and show loading
    const originalHtml = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    try {
        const response = await fetch(`/sql/projects/${projectUuid}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: newName.trim() })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        const updatedProject = await response.json();

        // Update project name in the UI
        projectNameElement.textContent = updatedProject.name;

        createAlert(`Proyecto actualizado con éxito.`, 'success');

    } catch (error) {
        console.error('Error updating project:', error);
        createAlert(`Error al actualizar el proyecto: ${error.message}`, 'danger');
        // Restore original name in case of error
        projectNameElement.textContent = originalName;
    } finally {
        // Re-enable button
        button.disabled = false;
        button.innerHTML = originalHtml;
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

document.addEventListener('DOMContentLoaded', loadUserProjects);