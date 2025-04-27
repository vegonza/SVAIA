const userTableBody = document.getElementById('user-table-body');
const notificationArea = document.getElementById('notification-area');

const alertTemplate = document.getElementById('alert-template');
const loadingTemplate = document.getElementById('loading-template');
const emptyTableTemplate = document.getElementById('empty-table-template');
const errorTemplate = document.getElementById('error-template');
const userRowTemplate = document.getElementById('user-row-template');

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

async function loadUsers() {
    // Show loading state
    userTableBody.innerHTML = '';
    userTableBody.appendChild(loadingTemplate.content.cloneNode(true));

    try {
        const response = await fetch('/sql/users/all');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const users = await response.json();

        // Clear the table
        userTableBody.innerHTML = '';

        if (users.length === 0) {
            userTableBody.appendChild(emptyTableTemplate.content.cloneNode(true));
            return;
        }

        users.forEach(user => {
            // Clone the user row template
            const rowNode = userRowTemplate.content.cloneNode(true);
            const row = rowNode.querySelector('tr');

            // Fill in the user data
            row.querySelector('.user-id').textContent = user.id;
            row.querySelector('.user-name').textContent = user.name || 'N/A';
            row.querySelector('.user-last-name').textContent = user.last_name || 'N/A';
            row.querySelector('.user-email').textContent = user.email;

            const roleCell = row.querySelector('.user-role');
            if (user.is_admin) {
                roleCell.textContent = 'Admin';
            } else {
                roleCell.textContent = 'Usuario';
            }

            // Set up the action buttons
            const viewProjectsButton = row.querySelector('.view-projects-btn');
            viewProjectsButton.setAttribute('data-user-id', user.id);
            viewProjectsButton.setAttribute('data-name', user.name);

            const editButton = row.querySelector('.edit-btn');
            editButton.href = editUserUrl.replace('0', user.id);

            const deleteForm = row.querySelector('form');
            deleteForm.action = deleteUserUrl.replace('0', user.id);

            // Add event listeners
            viewProjectsButton.addEventListener('click', () => {
                window.location.href = `/admin/user-projects/${viewProjectsButton.getAttribute('data-user-id')}`;
            });

            deleteForm.addEventListener('submit', (event) => {
                if (!confirm('¿Estás seguro de que deseas eliminar este usuario? Esta acción no se puede deshacer.')) {
                    event.preventDefault();
                }
            });

            // Add the row to the table
            userTableBody.appendChild(rowNode);
        });

    } catch (error) {
        console.error('Error loading users:', error);
        userTableBody.innerHTML = '';
        userTableBody.appendChild(errorTemplate.content.cloneNode(true));
        createAlert('Error al cargar la lista de usuarios.', 'danger');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});