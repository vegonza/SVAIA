const chat = document.getElementById("chat-messages");
const inputText = document.getElementById("message-input");
const template_user = document.getElementById("user-message-template");
const template_ai = document.getElementById("ai-message-template");
const template_project = document.getElementById("project-template");
const template_mobile_project = document.getElementById("mobile-project-template");
const new_chat = document.getElementById("new-chat");
const project_list = document.getElementById("project-list");
const mobile_project_list = document.getElementById("mobile-project-list");
let total = 0;
let loading = false;

async function get_response(message) {
    return fetch("/chat/completion", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    })
        .then(res => {
            if (!res.ok) {
                throw new Error('Error: ' + res.statusText);
            }
            return res.json();
        })
        .then(data => {
            return data.message;
        })
        .catch(error => {
            console.error('Error:', error);
            return "Sorry, there was an error processing your request.";
        });
}

function create_message(input, isUser = false) {
    const template = isUser ? template_user : template_ai;
    const clone = template.content.cloneNode(true);
    const messageDiv = clone.querySelector(".message-content");
    messageDiv.textContent = input;

    const message = document.createElement("div");
    message.id = `message-${total}`;
    message.appendChild(clone);
    chat.appendChild(message);
}

async function sendMessage() {
    if (loading) {
        return;
    }
    loading = true;
    const input = inputText.value.trim();
    if (!input) {
        return;
    }
    inputText.value = "";
    create_message(input, isUser = true);
    try {
        const response = await get_response(input);
        console.log(response);
        create_message(response);
    } catch (error) {
        create_message("Ha habido un error en el servidor");
    }
    inputText.focus();
    chat.scrollTop = chat.scrollHeight;
    total++;
    loading = false;
}

async function get_projects() {
    // clear lists
    project_list.innerHTML = '';
    mobile_project_list.innerHTML = '<option value="" disabled selected>Select a project</option>';

    return fetch("/sql/projects")
        .then(res => {
            return res.json();
        })
        .then(data => {
            data.forEach((project, index) => {
                // Desktop version
                const clone = template_project.content.cloneNode(true);
                const projectDiv = clone.querySelector(".conversation");
                const projectName = projectDiv.querySelector(".project-name");
                const deleteBtn = projectDiv.querySelector(".delete-conversation");
                projectName.textContent = project.name;

                // Remove active class for even items (0-based index)
                if (index % 2 === 0) {
                    projectDiv.classList.remove("active");
                }

                projectDiv.addEventListener("click", (e) => {
                    // Only load project if not clicking the delete button
                    if (!e.target.closest('.delete-conversation')) {
                        console.log(project.uuid);
                        load_project(project.uuid);
                    }
                });

                // Add delete button event listener
                deleteBtn.addEventListener("click", (e) => {
                    e.stopPropagation(); // Prevent bubbling to parent click
                    if (confirm("Are you sure you want to delete this project?")) {
                        delete_project(project.uuid, projectDiv.parentElement);
                    }
                });

                project_list.appendChild(clone);

                // Mobile version
                const mobileClone = template_mobile_project.content.cloneNode(true);
                const mobileOption = mobileClone.querySelector(".project-option");
                mobileOption.value = project.uuid;
                mobileOption.textContent = project.name;
                mobile_project_list.appendChild(mobileClone);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            return [];
        });
}

async function load_project(uuid) {
    return fetch(`/sql/projects/${uuid}`)
        .then(res => {
            return res.json();
        })
        .then(data => {
            console.log(data);
        });
}

async function delete_project(uuid, element) {
    fetch(`/sql/projects/${uuid}`, {
        method: 'DELETE'
    })
        .then(res => {
            if (res.ok) {
                get_projects();
                return res.json();
            }
            throw new Error('Failed to delete project');
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

async function create_project() {
    return fetch("/sql/projects", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: "New Project" })
    })
        .then(res => {
            console.log(res);
            return res.json();
        })
        .then(data => {
            // Refresh the project list
            get_projects();
            return data;
        });
}

inputText.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

new_chat.addEventListener("click", () => {
    console.log("new chat");
    create_project();
});

document.addEventListener("DOMContentLoaded", function () {
    get_projects();
    create_message("Hola usuario");
});