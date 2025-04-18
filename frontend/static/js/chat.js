const chat = document.getElementById("chat-messages");
const input_text = document.getElementById("message-input");
const user_template = document.getElementById("user-message-template");
const ai_template = document.getElementById("ai-message-template");
const project_template = document.getElementById("project-template");
const mobile_project_template = document.getElementById("mobile-project-template");
const new_chat_btn = document.getElementById("new-chat");
const project_list = document.getElementById("project-list");
const mobile_project_list = document.getElementById("mobile-project-list");
const warning_alert = document.getElementById("warning-alert");
const warning_message = document.getElementById("warning-message");
let message_counter = 0;
let loading = false;
let current_project_uuid = null;

function show_warning(message) {
    warning_message.textContent = message;
    warning_alert.classList.remove("d-none");
}

function check_url_for_project() {
    const url_params = new URLSearchParams(window.location.search);
    const project_uuid = url_params.get('project');
    if (project_uuid) {
        current_project_uuid = project_uuid;
        load_project(project_uuid);
    }
}

function update_url(uuid) {
    const url = new URL(window.location);
    url.searchParams.set('project', uuid);
    window.history.pushState({}, '', url);
}

function create_message(content, is_user = false) {
    const template = is_user ? user_template : ai_template;
    const clone = template.content.cloneNode(true);
    const message_div = clone.querySelector(".message-content");

    if (!is_user && window.marked) {
        marked.setOptions({
            breaks: true,
            tables: true,
            smartLists: true,
            headerIds: false,
        });

        try {
            message_div.innerHTML = marked.parse(content);
        } catch (error) {
            console.error('Error parsing markdown:', error);
            message_div.textContent = content;
        }
    } else {
        message_div.textContent = content;
    }

    const message = document.createElement("div");
    message.id = `message-${message_counter}`;
    message.appendChild(clone);
    chat.appendChild(message);
}

function clear_chat() {
    chat.innerHTML = '';
    message_counter = 0;
}

function display_messages(messages) {
    clear_chat();
    if (messages && messages.length > 0) {
        messages.forEach(message => {
            create_message(message.content, message.is_user);
            message_counter++;
        });
    }
    chat.scrollTop = chat.scrollHeight;
}

async function send_message() {
    if (loading || !current_project_uuid) {
        return;
    }

    loading = true;
    const input = input_text.value.trim();

    if (!input) {
        loading = false;
        return;
    }

    input_text.value = "";
    create_message(input, true);

    try {
        const response_id = message_counter++;
        const placeholder = document.createElement("div");
        placeholder.id = `message-${response_id}`;

        const template = ai_template.content.cloneNode(true);
        const message_div = template.querySelector(".message-content");
        message_div.id = `content-${response_id}`;

        placeholder.appendChild(template);
        chat.appendChild(placeholder);
        chat.scrollTop = chat.scrollHeight;

        const response = await fetch('/chat/completion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: input,
                project_uuid: current_project_uuid
            })
        });

        if (!response.ok) {
            throw new Error(`El servidor respondió con ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let full_content = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));

                        if (data.done) {
                            const content_div = document.getElementById(`content-${response_id}`);
                            if (content_div) {
                                try {
                                    if (window.marked) {
                                        marked.setOptions({
                                            breaks: true,
                                            tables: true,
                                            smartLists: true,
                                        });
                                        content_div.innerHTML = marked.parse(data.full_content);
                                    } else {
                                        content_div.textContent = data.full_content;
                                    }
                                } catch (error) {
                                    console.error('Error parsing markdown:', error);
                                    content_div.textContent = data.full_content;
                                }
                            }
                            break;
                        }

                        if (data.chunk) {
                            full_content += data.chunk;

                            const content_div = document.getElementById(`content-${response_id}`);
                            if (content_div) {
                                try {
                                    if (window.marked) {
                                        marked.setOptions({
                                            breaks: true,
                                            tables: true,
                                            smartLists: true,
                                        });
                                        content_div.innerHTML = marked.parse(full_content) + "<span class='typing-cursor'>▋</span>";
                                    } else {
                                        content_div.textContent = full_content;
                                    }
                                } catch (error) {
                                    console.error('Error parsing markdown:', error);
                                    content_div.textContent = full_content;
                                }

                                chat.scrollTop = chat.scrollHeight;
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e, line);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        create_message("Ha ocurrido un error en el servidor. Por favor, inténtalo de nuevo.");
    }

    input_text.focus();
    loading = false;
}

async function get_projects() {
    project_list.innerHTML = '';
    mobile_project_list.innerHTML = '<option value="" disabled selected>Seleccionar proyecto</option>';

    try {
        const response = await fetch("/sql/projects");
        const projects = await response.json();

        projects.forEach((project, index) => {
            // Desktop version
            const clone = project_template.content.cloneNode(true);
            const project_div = clone.querySelector(".conversation");
            const project_name = project_div.querySelector(".project-name");
            const delete_btn = project_div.querySelector(".delete-conversation");
            project_name.textContent = project.name;

            if (index % 2 !== 0) {
                project_div.classList.add("active");
            } else {
                project_div.classList.remove("active");
            }

            project_div.addEventListener("click", (e) => {
                if (!e.target.closest('.delete-conversation')) {
                    load_project(project.uuid);
                }
            });

            delete_btn.addEventListener("click", (e) => {
                e.stopPropagation();
                if (confirm("Confirmar")) {
                    delete_project(project.uuid);
                }
            });

            project_list.appendChild(clone);

            // Mobile version
            const mobile_clone = mobile_project_template.content.cloneNode(true);
            const mobile_option = mobile_clone.querySelector(".project-option");
            mobile_option.value = project.uuid;
            mobile_option.textContent = project.name;

            if (project.uuid === current_project_uuid) {
                mobile_option.selected = true;
            }

            mobile_project_list.appendChild(mobile_clone);
        });

        mobile_project_list.addEventListener('change', function () {
            const selected_uuid = this.value;
            if (selected_uuid) {
                load_project(selected_uuid);
            }
        });
    } catch (error) {
        console.error('Error loading projects:', error);
        show_warning("Error al cargar los proyectos.");
    }
}

async function load_project(uuid) {
    current_project_uuid = uuid;
    update_url(uuid);

    try {
        const response = await fetch(`/sql/projects/${uuid}`);
        const data = await response.json();

        if (data.messages) {
            display_messages(data.messages);
        } else {
            clear_chat();
        }

        get_projects();
    } catch (error) {
        console.error('Error loading project:', error);
        show_warning("Error al cargar el proyecto: " + error.message);
    }
}

async function delete_project(uuid) {
    try {
        const response = await fetch(`/sql/projects/${uuid}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            if (uuid === current_project_uuid) {
                current_project_uuid = null;
                clear_chat();
                const url = new URL(window.location);
                url.searchParams.delete('project');
                window.history.pushState({}, '', url);
            }
            get_projects();
        } else {
            throw new Error('No se pudo eliminar el proyecto');
        }
    } catch (error) {
        console.error('Error deleting project:', error);
        show_warning("Error al eliminar el proyecto: " + error.message);
    }
}

async function create_project() {
    const project_name = prompt("Ingresa un nombre para el proyecto:", "Nuevo Proyecto");

    if (project_name === null) {
        return;
    }

    try {
        const response = await fetch("/sql/projects", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: project_name })
        });

        if (!response.ok) {
            throw new Error('Error al crear el proyecto: ' + response.statusText);
        }

        const data = await response.json();
        load_project(data.uuid);
    } catch (error) {
        console.error('Error creating project:', error);
        show_warning("Error al crear el proyecto: " + error.message);
    }
}

input_text.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        send_message();
    }
});

mobile_project_list.addEventListener('change', function () {
    const selected_uuid = this.value;
    if (selected_uuid) {
        load_project(selected_uuid);
    }
});

new_chat_btn.addEventListener("click", () => {
    create_project();
});

document.addEventListener("DOMContentLoaded", function () {
    get_projects();
    check_url_for_project();
});