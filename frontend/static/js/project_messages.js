const chatMessages = document.getElementById('chat-messages');
const projectName = document.getElementById('project-name');
const breadcrumbProjectName = document.getElementById('breadcrumb-project-name');
const backButton = document.getElementById('back-button');
const backToProjects = document.getElementById('back-to-projects');
const breadcrumbUsername = document.getElementById('breadcrumb-username');
const notificationArea = document.getElementById('notification-area');
const userMessageTemplate = document.getElementById('user-message-template');
const aiMessageTemplate = document.getElementById('ai-message-template');

const alertTemplate = document.getElementById('alert-template');
const loadingTemplate = document.getElementById('loading-template');
const emptyMessagesTemplate = document.getElementById('empty-messages-template');
const errorTemplate = document.getElementById('error-template');

let messageCounter = 0;
let userId = null;
let currentProject = null;

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

function clearChat() {
    chatMessages.innerHTML = '';
    messageCounter = 0;
}

function createMessage(content, isUser = false) {
    const template = isUser ? userMessageTemplate : aiMessageTemplate;
    const clone = template.content.cloneNode(true);
    const messageDiv = clone.querySelector(".message-content");

    if (!isUser && window.marked) {
        marked.setOptions({
            breaks: true,
            tables: true,
            smartLists: true,
            headerIds: false,
        });

        try {
            messageDiv.innerHTML = marked.parse(content);
        } catch (error) {
            console.error('Error parsing markdown:', error);
            messageDiv.textContent = content;
        }
    } else {
        messageDiv.textContent = content;
    }

    const message = document.createElement("div");
    message.id = `message-${messageCounter++}`;
    message.appendChild(clone);
    chatMessages.appendChild(message);
}

function displayMessages(messages) {
    clearChat();
    if (messages && messages.length > 0) {
        messages.forEach(message => {
            createMessage(message.content, message.is_user);
        });
    } else {
        chatMessages.innerHTML = '';
        chatMessages.appendChild(emptyMessagesTemplate.content.cloneNode(true));
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function loadProject() {
    try {
        const response = await fetch(`/sql/projects/${projectUuid}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentProject = data;

        // Set project name
        projectName.textContent = data.name;
        breadcrumbProjectName.textContent = data.name;
        document.title = `SVAIA - Mensajes de ${data.name}`;

        // Set user ID for back button
        userId = data.user_id;

        // Get username and update breadcrumb
        const userResponse = await fetch(`/sql/users/all`);
        if (userResponse.ok) {
            const users = await userResponse.json();
            const user = users.find(u => u.id === userId);
            if (user) {
                breadcrumbUsername.textContent = user.username;
            }
        }

        // Display messages
        if (data.messages) {
            displayMessages(data.messages);
        } else {
            chatMessages.innerHTML = '';
            chatMessages.appendChild(emptyMessagesTemplate.content.cloneNode(true));
        }

        // Set up back button
        backButton.addEventListener('click', () => {
            window.location.href = `/admin/user-projects/${userId}`;
        });

        backToProjects.href = `/admin/user-projects/${userId}`;

    } catch (error) {
        console.error('Error loading project:', error);
        projectName.textContent = 'Error al cargar el proyecto';
        chatMessages.innerHTML = '';
        chatMessages.appendChild(errorTemplate.content.cloneNode(true));
        createAlert(`Error: ${error.message}`);
    }
}

document.addEventListener('DOMContentLoaded', loadProject);