const chat = document.getElementById("chat-messages");
const input_text = document.getElementById("message-input");
const new_chat_btn = document.getElementById("new-chat");
const project_list = document.getElementById("project-list");
const warning_alert = document.getElementById("warning-alert");
const warning_message = document.getElementById("warning-message");
const projectModal = new bootstrap.Modal(document.getElementById('projectModal'));
const projectModalElement = document.getElementById('projectModal');
const projectForm = document.getElementById('projectForm');
const projectUuidInput = document.getElementById('projectUuid');
const projectNameInput = document.getElementById('projectName');
const projectDescriptionInput = document.getElementById('projectDescription');
const saveProjectBtn = document.getElementById('saveProjectBtn');
const projectModalLabel = document.getElementById('projectModalLabel');

// File upload elements
const fileUploadSection = document.getElementById('fileUploadSection');
const dockerfilesInput = document.getElementById('dockerfiles');
const dockerComposeFilesInput = document.getElementById('dockerComposeFiles');
const dockerImagesInput = document.getElementById('dockerImages');

// Vulnerability dropdown elements
const vulnerabilityDropdown = document.getElementById('vulnerabilityDropdown');
const selectedVulnerabilityInput = document.getElementById('selectedVulnerability');
const customVulnerabilityInput = document.getElementById('customVulnerability');

// Total vulnerabilities and solvability criteria elements
const totalVulnerabilitiesInput = document.getElementById('totalVulnerabilities');
const solvabilityDropdown = document.getElementById('solvabilityDropdown');
const selectedSolvabilityInput = document.getElementById('selectedSolvability');

// Save button elements
const saveButtonText = document.getElementById('saveButtonText');
const saveButtonSpinner = document.getElementById('saveButtonSpinner');

const user_template = document.getElementById("user-message-template");
const ai_template = document.getElementById("ai-message-template");
const project_template = document.getElementById("project-template");
const mobile_project_template = document.getElementById("mobile-project-template");

let message_counter = 0;
let loading = false;
let current_project_uuid = null;
let isEditMode = false;
let mobile_project_list = document.getElementById("mobile-project-list");

// Initialize mermaid with more robust configuration
if (window.mermaid) {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'trebuchet ms, verdana, arial, sans-serif',
        logLevel: 'error',
        flowchart: {
            htmlLabels: true,
            curve: 'linear',
            useMaxWidth: false,
            diagramPadding: 8
        },
        er: { useMaxWidth: false },
        sequence: { useMaxWidth: false, wrap: true, diagramMarginX: 50, diagramMarginY: 10 },
        gantt: { useMaxWidth: false }
    });
}

// Initialize dropdown functionality
function initializeDropdown() {
    // Vulnerability dropdown initialization
    const dropdownContent = document.querySelector('#vulnerabilityLevelSection .dropdown-content');
    if (dropdownContent) {
        const dropdownOptions = dropdownContent.querySelectorAll('a[data-value]');
        const customVulnerabilityContainer = document.getElementById('customVulnerabilityContainer');
        const dropdown = document.querySelector('#vulnerabilityLevelSection .dropdown');

        // Toggle dropdown on button click
        vulnerabilityDropdown.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });

        dropdownOptions.forEach(option => {
            option.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                const value = this.getAttribute('data-value');
                const text = this.textContent.trim();

                vulnerabilityDropdown.textContent = text;

                if (value === 'custom') {
                    // Show custom input and clear the hidden field
                    customVulnerabilityContainer.style.display = 'block';
                    selectedVulnerabilityInput.value = '';
                    customVulnerabilityInput.value = '';
                    customVulnerabilityInput.focus();
                } else {
                    // Hide custom input and set the selected value
                    customVulnerabilityContainer.style.display = 'none';
                    selectedVulnerabilityInput.value = value;
                    customVulnerabilityInput.value = '';
                }

                dropdown.classList.remove('show');
            });
        });

        customVulnerabilityInput.addEventListener('input', function () {
            if (this.value.trim()) {
                selectedVulnerabilityInput.value = this.value.trim();
            } else {
                selectedVulnerabilityInput.value = '';
            }
        });
    }
    
    // Solvability dropdown initialization
    const solvabilityDropdownContent = document.querySelector('#solvabilityCriteriaSection .dropdown-content');
    if (solvabilityDropdownContent && solvabilityDropdown) {
        const solvabilityOptions = solvabilityDropdownContent.querySelectorAll('a[data-value]');
        const solvabilityDropdownContainer = document.querySelector('#solvabilityCriteriaSection .dropdown');
        
        solvabilityDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            solvabilityDropdownContainer.classList.toggle('show');
        });
        
        solvabilityOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const value = this.getAttribute('data-value');
                const text = this.textContent.trim();
                
                solvabilityDropdown.textContent = text;
                selectedSolvabilityInput.value = value;
                
                solvabilityDropdownContainer.classList.remove('show');
            });
        });
    }

    // Close all dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });
}

function validateForm() {
    const name = projectNameInput.value.trim();
    const vulnerabilityLevel = selectedVulnerabilityInput.value.trim() || customVulnerabilityInput.value.trim();

    if (!name) {
        alert('El nombre del proyecto es obligatorio');
        return false;
    }

    if (!vulnerabilityLevel) {
        alert('Debe seleccionar un grado de vulnerabilidad');
        return false;
    }

    return true;
}

async function uploadFiles(projectUuid) {
    try {
        // Upload Dockerfiles
        if (dockerfilesInput.files.length > 0) {
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
        if (dockerComposeFilesInput.files.length > 0) {
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
        if (dockerImagesInput.files.length > 0) {
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

function setSaveButtonLoading(loading) {
    if (loading) {
        saveButtonText.textContent = 'Guardando...';
        saveButtonSpinner.classList.remove('d-none');
        saveProjectBtn.disabled = true;
    } else {
        saveButtonText.textContent = 'Guardar';
        saveButtonSpinner.classList.add('d-none');
        saveProjectBtn.disabled = false;
    }
}

function show_warning(message) {
    warning_message.textContent = message;
    warning_alert.classList.remove("d-none");
}

/**
 * Pre-processes mermaid syntax to fix common issues
 */
function fixMermaidSyntax(content) {
    if (!content) return content;

    console.log('Original mermaid content:', content);

    let fixed = content
        // Fix connection issues: ensure proper arrow syntax
        .replace(/--(?!\>)/g, '-->') // Replace -- with --> when not followed by >
        .replace(/\s+--\>/g, '-->') // Remove spaces before -->
        .replace(/--\>\s+/g, '-->') // Remove spaces after -->

        // Fix labels with spaces
        .replace(/\|([^|]*)\s+([^|]*)\|/g, function (match, p1, p2) {
            return `|${p1}${p2}|`.replace(/\s+/g, '_');
        })

        // Remove parentheses in node names (common error)
        .replace(/\[\[([^\]]*)\(([^\)]*)\)([^\]]*)\]\]/g, function (match, p1, p2, p3) {
            return `[[${p1 || ''}_${p2 || ''}_${p3 || ''}]]`;
        })
        .replace(/\[([^\]]*)\(([^\)]*)\)([^\]]*)\]/g, function (match, p1, p2, p3) {
            return `[${p1 || ''}_${p2 || ''}_${p3 || ''}]`;
        })

        // Fix subgraph syntax
        .replace(/subgraph\s+([^\s\[\]]+)\s*\[([^\]]+)\]/g, 'subgraph $1["$2"]')

        // Ensure node definitions are proper
        .replace(/([a-zA-Z0-9_-]+)(\s*\[\[|\s*\[\(|\s*\[)/g, '$1$2')

        // Normalize flowchart direction if missing or invalid
        .replace(/^graph\s+$/m, 'graph TD')
        .replace(/^flowchart\s+$/m, 'flowchart TD');

    // Split into lines for additional fixes
    let lines = fixed.split('\n');
    let fixedLines = [];
    let nodeNames = new Set();

    // Extract node names and validate connections
    for (let line of lines) {
        // Extract node names from definitions
        const nodeDefMatch = line.match(/^\s*([a-zA-Z0-9_-]+)\s*(\[\[|\[|\(\(|\()/);
        if (nodeDefMatch) {
            nodeNames.add(nodeDefMatch[1]);
        }

        // Collect cleaned lines
        fixedLines.push(line);
    }

    // Combine back into a string
    fixed = fixedLines.join('\n');

    console.log('Fixed mermaid content:', fixed);
    return fixed;
}

function render_mermaid_diagrams(container) {
    if (!window.mermaid) return;

    // Return a promise that resolves when all diagrams are rendered or rejects on failure
    return new Promise((resolve, reject) => {
        // Look specifically for ```mermaid``` code blocks in the HTML
        const mermaidBlocks = container.querySelectorAll('pre code');
        const renderPromises = [];

        mermaidBlocks.forEach((codeBlock, index) => {
            let content = codeBlock.textContent.trim();

            // Check if this is a mermaid diagram (starts with graph, flowchart, etc.)
            const mermaidPattern = /^(graph|flowchart|sequenceDiagram|classDiagram|erDiagram|gantt|pie|journey|gitgraph)\s/;

            if (mermaidPattern.test(content)) {
                // Fix common syntax issues before rendering
                content = fixMermaidSyntax(content);

                const diagramId = `mermaid-diagram-${Date.now()}-${index}`;

                // Create container for the mermaid diagram
                const diagramDiv = document.createElement('div');
                diagramDiv.id = diagramId;
                diagramDiv.className = 'mermaid-diagram';

                // Replace the code block with the diagram
                const preElement = codeBlock.closest('pre');
                if (preElement) {
                    preElement.parentNode.insertBefore(diagramDiv, preElement);
                    preElement.remove();

                    // Add this rendering to our promises array
                    renderPromises.push(
                        new Promise((resolveRender, rejectRender) => {
                            try {
                                // Temporarily replace troublesome syntax (backup approach)
                                let contentToRender = content;

                                // Attempt to parse and validate with mermaid
                                try {
                                    mermaid.parse(contentToRender);
                                    console.log('Mermaid syntax validation passed');
                                } catch (parseError) {
                                    console.warn('Mermaid syntax validation failed, applying additional fixes:', parseError);
                                    // Try to fix more aggressively if parsing fails
                                    contentToRender = contentToRender
                                        // Fix template literals that weren't properly processed
                                        .replace(/\$\{[^}]*\}/g, 'X')
                                        .replace(/\s*--+\s*/g, ' --> ') // More aggressive arrow fix
                                        .replace(/([^\s>])-->/g, '$1 -->') // Ensure space before arrows
                                        .replace(/-->([^\s])/g, '--> $1') // Ensure space after arrows
                                        // Fix port labels in connections
                                        .replace(/\|([^|]*)\s+([^|]*)\|/g, '|$1_$2|') // Replace spaces with underscores in port labels
                                        .replace(/\|([^|]*)\$/g, '|p_') // Replace $ in port labels
                                        .replace(/\|([^|]*)%([^|]*)\|/g, '|$1p$2|'); // Replace % in port labels

                                    // As last resort, if still containing template literals, create minimal valid diagram
                                    if (contentToRender.includes('${')) {
                                        console.log('Template literals still detected, using fallback diagram');
                                        contentToRender = `graph TD
                                            A[[Frontend]]
                                            B[(Database)]
                                            A-->B
                                            classDef app fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
                                            classDef db fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
                                            class A app
                                            class B db`;
                                    }
                                }

                                // Render with fixed content
                                mermaid.render(diagramId + '-svg', contentToRender)
                                    .then(({ svg }) => {
                                        diagramDiv.innerHTML = svg;
                                        console.log('Successfully rendered mermaid diagram');
                                        resolveRender();
                                    })
                                    .catch(error => {
                                        console.error('Error rendering mermaid diagram:', error);
                                        console.error('Mermaid content that failed:', contentToRender);

                                        // Show error with original content
                                        diagramDiv.innerHTML = `
                                            <div class="alert alert-danger" role="alert">
                                                <h6><i class="bi bi-exclamation-triangle"></i> Error en diagrama Mermaid</h6>
                                                <p><strong>Error:</strong> ${error.message}</p>
                                                <details>
                                                    <summary>Ver código mermaid original</summary>
                                                    <pre><code>${content}</code></pre>
                                                </details>
                                                <small class="text-muted">El AI necesita generar sintaxis mermaid válida.</small>
                                            </div>
                                        `;
                                        rejectRender({
                                            message: error.message,
                                            content: content,
                                            fixedContent: contentToRender
                                        });
                                    });
                            } catch (error) {
                                console.error('Error initiating mermaid render:', error);
                                rejectRender({
                                    message: error.message,
                                    content: content
                                });
                            }
                        })
                    );
                }
            }
        });

        if (renderPromises.length === 0) {
            // No mermaid diagrams found, resolve immediately
            resolve();
            return;
        }

        // Wait for all diagrams to be processed
        Promise.allSettled(renderPromises).then(results => {
            const failures = results.filter(r => r.status === 'rejected');
            if (failures.length > 0) {
                // Return the first error
                reject(failures[0].reason);
            } else {
                resolve();
            }
        });
    });
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
            highlight: function (code, lang) {
                // Don't highlight mermaid code, let our renderer handle it
                if (lang === 'mermaid') {
                    return code;
                }
                return code;
            }
        });

        try {
            message_div.innerHTML = marked.parse(content);
            // Process mermaid diagrams after parsing markdown
            render_mermaid_diagrams(message_div);
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
        let is_in_tool_call = false;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        const content_div = document.getElementById(`content-${response_id}`);

                        if (data.done) {
                            if (content_div) {
                                // Remove all tool call indicators
                                const toolIndicators = content_div.querySelectorAll('.tool-call-indicator');
                                toolIndicators.forEach(indicator => indicator.remove());

                                // Clean the full content and render final markdown
                                try {
                                    if (window.marked) {
                                        marked.setOptions({
                                            breaks: true,
                                            tables: true,
                                            smartLists: true,
                                            highlight: function (code, lang) {
                                                if (lang === 'mermaid') {
                                                    return code;
                                                }
                                                return code;
                                            }
                                        });
                                        content_div.innerHTML = marked.parse(full_content);
                                        // Render mermaid diagrams in the final content
                                        render_mermaid_diagrams(content_div);
                                    } else {
                                        content_div.textContent = full_content;
                                    }
                                } catch (error) {
                                    console.error('Error parsing markdown:', error);
                                    content_div.textContent = full_content;
                                }
                            }
                            break;
                        }

                        if (data.type === 'text' && data.content) {
                            full_content += data.content;
                            is_in_tool_call = false;

                            if (content_div) {
                                try {
                                    if (window.marked) {
                                        marked.setOptions({
                                            breaks: true,
                                            tables: true,
                                            smartLists: true,
                                        });
                                        content_div.innerHTML = marked.parse(full_content) + "<span class='typing-cursor'>▋</span>";
                                        // Only render mermaid for final content to avoid flickering
                                    } else {
                                        content_div.textContent = full_content + "▋";
                                    }
                                } catch (error) {
                                    console.error('Error parsing markdown:', error);
                                    content_div.textContent = full_content + "▋";
                                }

                                chat.scrollTop = chat.scrollHeight;
                            }
                        }

                        if (data.type === 'tool_call' && data.tool_name) {
                            if (!is_in_tool_call) {
                                is_in_tool_call = true;

                                if (content_div) {
                                    // Create tool call indicator
                                    const tool_indicator = document.createElement('div');
                                    tool_indicator.className = 'tool-call-indicator mb-2 p-2 rounded';
                                    tool_indicator.style.cssText = `
                                        background: rgba(255, 193, 7, 0.1);
                                        border: 1px solid rgba(255, 193, 7, 0.3);
                                        color: #856404;
                                        font-size: 0.9em;
                                        display: flex;
                                        align-items: center;
                                        gap: 8px;
                                    `;

                                    tool_indicator.innerHTML = `
                                        <i class="bi bi-tools" style="color: #ffc107;"></i>
                                        <span>Ejecutando herramienta: <strong>${data.tool_name}</strong></span>
                                        <div class="spinner-border spinner-border-sm text-warning" role="status" style="width: 16px; height: 16px;">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                    `;

                                    content_div.appendChild(tool_indicator);
                                    chat.scrollTop = chat.scrollHeight;
                                }
                            }
                        }

                        if (data.type === 'error' && data.content) {
                            if (content_div) {
                                const error_div = document.createElement('div');
                                error_div.className = 'alert alert-danger mt-2';
                                error_div.innerHTML = `<i class="bi bi-exclamation-triangle"></i> Error: ${data.content}`;
                                content_div.appendChild(error_div);
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
        let currentProject = null;

        projects.forEach((project, index) => {
            // Desktop version
            const clone = project_template.content.cloneNode(true);
            const project_div = clone.querySelector(".conversation");
            const project_name = project_div.querySelector(".project-name");
            const project_description = project_div.querySelector(".project-description");
            const delete_btn = project_div.querySelector(".delete-conversation");

            project_name.textContent = project.name;
            project_description.textContent = project.description;

            if (index % 2 !== 0) {
                project_div.classList.add("active");
                project_div.classList.add("project-dark");
            } else {
                project_div.classList.remove("active");
            }

            // Create action buttons container if it doesn't exist
            let actionsDiv = delete_btn.parentElement;
            actionsDiv.className = "project-actions";

            // Add edit button
            const edit_btn = document.createElement('button');
            edit_btn.className = 'edit-conversation btn rounded-2 bg-warning text-white border-0 m-1';
            edit_btn.innerHTML = '<i class="bi bi-pencil"></i>';
            edit_btn.addEventListener('click', (e) => {
                e.stopPropagation();
                showEditProjectModal(project);
            });

            // Add the edit button before the delete button
            actionsDiv.insertBefore(edit_btn, delete_btn);

            project_div.addEventListener("click", (e) => {
                if (!e.target.closest('.delete-conversation') && !e.target.closest('.edit-conversation')) {
                    load_project(project.uuid);
                }
            });

            delete_btn.addEventListener("click", (e) => {
                e.stopPropagation();
                if (confirm("¿Estás seguro de que deseas eliminar este proyecto?")) {
                    delete_project(project.uuid);
                }
            });

            project_list.appendChild(clone);

            // Mobile version - dropdown with styled options
            const mobile_clone = mobile_project_template.content.cloneNode(true);
            const mobile_option = mobile_clone.querySelector(".project-option");
            mobile_option.value = project.uuid;

            // Apply alternating styles to option text
            if (index % 2 !== 0) {
                mobile_option.textContent = `🔹 ${project.name}`;
                mobile_option.style.backgroundColor = '#f8f9fa';
            } else {
                mobile_option.textContent = `⚪ ${project.name}`;
                mobile_option.style.backgroundColor = '#ffffff';
            }

            if (project.uuid === current_project_uuid) {
                mobile_option.selected = true;
                currentProject = project;
            }

            mobile_project_list.appendChild(mobile_clone);
        });

        // Handle mobile project selection and action buttons
        const mobileProjectActions = document.getElementById('mobile-project-actions');
        const editCurrentBtn = document.getElementById('edit-current-mobile-project');
        const deleteCurrentBtn = document.getElementById('delete-current-mobile-project');

        // Remove existing event listeners by cloning and replacing the element
        const new_mobile_list = mobile_project_list.cloneNode(true);
        mobile_project_list.parentNode.replaceChild(new_mobile_list, mobile_project_list);
        mobile_project_list = new_mobile_list;

        // Add the event listener for project selection
        mobile_project_list.addEventListener('change', function () {
            const selected_uuid = this.value;
            if (selected_uuid) {
                load_project(selected_uuid);
                // Show action buttons when a project is selected
                mobileProjectActions.style.display = 'flex';

                // Update current project reference
                currentProject = projects.find(p => p.uuid === selected_uuid);
            } else {
                mobileProjectActions.style.display = 'none';
                currentProject = null;
            }
        });

        // Show/hide action buttons based on current selection
        if (currentProject) {
            mobileProjectActions.style.display = 'flex';
        } else {
            mobileProjectActions.style.display = 'none';
        }

        // Add event listeners for action buttons
        editCurrentBtn.addEventListener('click', () => {
            if (currentProject) {
                showEditProjectModal(currentProject);
            }
        });

        deleteCurrentBtn.addEventListener('click', () => {
            if (currentProject) {
                if (confirm("¿Estás seguro de que deseas eliminar este proyecto?")) {
                    delete_project(currentProject.uuid);
                }
            }
        });

    } catch (error) {
        console.error('Error loading projects:', error);
        show_warning("Error al cargar los proyectos.");
    }
}

function showCreateProjectModal() {
    isEditMode = false;
    projectModalLabel.textContent = 'Nuevo Proyecto';
    projectUuidInput.value = '';
    projectNameInput.value = '';
    projectDescriptionInput.value = '';

    // Reset vulnerability dropdown and custom vulnerability
    vulnerabilityDropdown.textContent = 'Elegir';
    selectedVulnerabilityInput.value = '';
    customVulnerabilityInput.value = '';
    document.getElementById('customVulnerabilityContainer').style.display = 'none';

    // Reset total vulnerabilities and solvability
    if (totalVulnerabilitiesInput) totalVulnerabilitiesInput.value = '';
    if (solvabilityDropdown) {
        solvabilityDropdown.textContent = 'Elegir';
        selectedSolvabilityInput.value = '';
    }

    // Reset file inputs
    dockerfilesInput.value = '';
    dockerComposeFilesInput.value = '';
    dockerImagesInput.value = '';

    fileUploadSection.style.display = 'block';

    dockerfilesInput.required = false;
    dockerComposeFilesInput.required = false;
    dockerImagesInput.required = false;

    projectModal.show();
}

function showEditProjectModal(project) {
    isEditMode = true;
    projectModalLabel.textContent = 'Editar Proyecto';
    projectUuidInput.value = project.uuid;
    projectNameInput.value = project.name;
    projectDescriptionInput.value = project.description || '';

    const existingVulnerability = project.vulnerability_level || '';
    if (existingVulnerability) {
        const predefinedValues = {
            'critical': 'Grado de vulnerabilidad crítico (8-10)',
            'severe': 'Grado de vulnerabilidad severa (6-7)',
            'mild': 'Grado de vulnerabilidad leve o medio (1-5)'
        };

        if (predefinedValues[existingVulnerability]) {
            vulnerabilityDropdown.textContent = predefinedValues[existingVulnerability];
            selectedVulnerabilityInput.value = existingVulnerability;
            customVulnerabilityInput.value = '';
            document.getElementById('customVulnerabilityContainer').style.display = 'none';
        } else {
            vulnerabilityDropdown.textContent = 'Otro (especificar)';
            selectedVulnerabilityInput.value = existingVulnerability;
            customVulnerabilityInput.value = existingVulnerability;
            document.getElementById('customVulnerabilityContainer').style.display = 'block';
        }
    } else {
        vulnerabilityDropdown.textContent = 'Elegir';
        selectedVulnerabilityInput.value = '';
        customVulnerabilityInput.value = '';
        document.getElementById('customVulnerabilityContainer').style.display = 'none';
    }

    // Set total vulnerabilities value
    if (totalVulnerabilitiesInput) {
        totalVulnerabilitiesInput.value = project.total_vulnerabilities_criteria || '';
    }
    
    // Set solvability criteria
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
    } else if (solvabilityDropdown) {
        solvabilityDropdown.textContent = 'Elegir';
        selectedSolvabilityInput.value = '';
    }

    dockerfilesInput.value = '';
    dockerComposeFilesInput.value = '';
    dockerImagesInput.value = '';

    fileUploadSection.style.display = 'block';

    dockerfilesInput.required = false;
    dockerComposeFilesInput.required = false;
    dockerImagesInput.required = false;

    projectModal.show();
}

async function saveProject() {
    if (!validateForm()) {
        return;
    }

    setSaveButtonLoading(true);

    const name = projectNameInput.value.trim();
    const description = projectDescriptionInput.value.trim();
    const vulnerabilityLevel = selectedVulnerabilityInput.value.trim() || customVulnerabilityInput.value.trim();
    const uuid = projectUuidInput.value;
    
    // Get total vulnerabilities value
    const totalVulnerabilities = totalVulnerabilitiesInput && totalVulnerabilitiesInput.value.trim() ? 
        parseInt(totalVulnerabilitiesInput.value.trim()) : null;
    
    // Get solvability criteria
    const solvabilityCriteria = selectedSolvabilityInput ? selectedSolvabilityInput.value.trim() : '';

    try {
        let response;
        let data;

        if (isEditMode) {
            // Update existing project
            response = await fetch(`/sql/projects/${uuid}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    vulnerability_level: vulnerabilityLevel,
                    total_vulnerabilities_criteria: totalVulnerabilities,
                    solvability_criteria: solvabilityCriteria
                })
            });
        } else {
            // Create new project
            response = await fetch("/sql/projects", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    description: description,
                    vulnerability_level: vulnerabilityLevel,
                    total_vulnerabilities_criteria: totalVulnerabilities,
                    solvability_criteria: solvabilityCriteria
                })
            });
        }

        if (!response.ok) {
            throw new Error('Error al guardar el proyecto: ' + response.statusText);
        }

        data = await response.json();

        // Upload files if any are selected (for both create and edit modes)
        const hasFiles = dockerfilesInput.files.length > 0 ||
            dockerComposeFilesInput.files.length > 0 ||
            dockerImagesInput.files.length > 0;

        if (hasFiles) {
            try {
                const projectUuid = isEditMode ? uuid : data.uuid;
                await uploadFiles(projectUuid);
            } catch (uploadError) {
                const message = isEditMode ?
                    'Proyecto actualizado, pero hubo un error al subir algunos archivos: ' + uploadError.message :
                    'Proyecto creado, pero hubo un error al subir algunos archivos: ' + uploadError.message;

                show_warning(message + ' Puedes intentar subir los archivos editando el proyecto.');
                projectModal.hide();
                await get_projects();

                if (!isEditMode) {
                    load_project(data.uuid);
                }
                return;
            }
        }

        projectModal.hide();
        await get_projects();

        if (!isEditMode) {
            load_project(data.uuid);
            // If files were uploaded, initialize project analysis
            if (hasFiles) {
                setTimeout(() => {
                    init_project_analysis(data.uuid);
                }, 1000); // Small delay to ensure project is loaded
            }
        }

    } catch (error) {
        console.error('Error saving project:', error);
        show_warning("Error al guardar el proyecto: " + error.message);
    } finally {
        setSaveButtonLoading(false);
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
    } catch (error) {
        console.error('Error loading project:', error);
        show_warning("Error al cargar el proyecto: " + error.message);
    }
}

async function init_project_analysis(uuid, retryCount = 0, errorInfo = null) {
    if (!uuid) return;

    // Max retries for mermaid rendering
    const MAX_RETRIES = 3;
    const loadingId = `loading-${Date.now()}`;

    try {
        // Show a loading message with animation
        const loadingMessage = document.createElement("div");
        loadingMessage.id = loadingId;
        loadingMessage.innerHTML = `
            <li class="d-flex align-items-start mb-3 container-fluid pe-0">
                <i class="bi bi-robot me-4"></i>
                <div class="bg-secondary text-white p-4 rounded-2 container-fluid">
                    <div class="d-flex align-items-center">
                        <div class="spinner-border text-light me-3" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span>${retryCount > 0 ? `Reintentando análisis (${retryCount}/${MAX_RETRIES})...` : 'Analizando proyecto y generando diagrama de arquitectura...'}</span>
                    </div>
                </div>
            </li>
        `;

        // Remove any previous loading message if this is a retry
        if (retryCount > 0) {
            const messages = chat.children;
            for (let i = 0; i < messages.length; i++) {
                if (messages[i].id && messages[i].id.startsWith('loading-')) {
                    chat.removeChild(messages[i]);
                    break;
                }
            }
        } else {
            // Clear any previous message that might exist
            const existingMessages = chat.querySelectorAll('div[id^="message-"]');
            if (existingMessages.length > 0 && existingMessages[existingMessages.length - 1].querySelector('.message-content')?.textContent.includes('Iniciando análisis')) {
                chat.removeChild(existingMessages[existingMessages.length - 1]);
            }
        }

        chat.appendChild(loadingMessage);
        chat.scrollTop = chat.scrollHeight;

        // Build request body with error information if available
        const requestBody = {
            project_uuid: uuid
        };

        if (errorInfo) {
            requestBody.error_info = errorInfo;
        }

        const response = await fetch('/chat/init-project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }

        // Instead of streaming, collect the entire response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let completeResponse = '';
        let finalContent = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            completeResponse += decoder.decode(value, { stream: true });
        }

        // Process the collected SSE data to extract the final content
        const lines = completeResponse.split('\n\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.substring(6));
                    if (data.done && data.full_content) {
                        finalContent = data.full_content;
                        break;
                    } else if (data.type === 'text' && data.content) {
                        finalContent += data.content;
                    } else if (data.type === 'error' && data.content) {
                        throw new Error(data.content);
                    }
                } catch (e) {
                    console.error('Error parsing SSE data:', e, line);
                }
            }
        }

        // Remove the loading message
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            chat.removeChild(loadingElement);
        }

        // Create the message with the complete content
        const messageId = message_counter++;
        const messageElement = document.createElement("div");
        messageElement.id = `message-${messageId}`;

        const template = ai_template.content.cloneNode(true);
        const contentDiv = template.querySelector(".message-content");
        contentDiv.id = `content-${messageId}`;

        // Render markdown
        if (window.marked) {
            marked.setOptions({
                breaks: true,
                tables: true,
                smartLists: true,
                highlight: function (code, lang) {
                    // Don't highlight mermaid code, let our renderer handle it
                    if (lang === 'mermaid') {
                        return code;
                    }
                    return code;
                }
            });
            try {
                contentDiv.innerHTML = marked.parse(finalContent);
            } catch (error) {
                console.error('Error parsing markdown:', error);
                contentDiv.textContent = finalContent;
            }
        } else {
            contentDiv.textContent = finalContent;
        }

        messageElement.appendChild(template);
        chat.appendChild(messageElement);
        chat.scrollTop = chat.scrollHeight;

        // Now try to render mermaid diagrams
        try {
            await render_mermaid_diagrams(contentDiv);
            console.log('Successfully rendered all mermaid diagrams');
        } catch (mermaidError) {
            console.error('Error rendering mermaid diagram:', mermaidError);

            // If we haven't reached max retries, try again
            if (retryCount < MAX_RETRIES - 1) {
                // Remove the message that failed rendering
                chat.removeChild(messageElement);

                // Prepare detailed error information for the backend
                const errorInfo = {
                    message: mermaidError.message || 'Unknown error',
                    content: mermaidError.content || '',
                    fixedContent: mermaidError.fixedContent || '',
                    retry_count: retryCount + 1,
                    syntax_details: mermaidError.syntax_details || 'Invalid syntax',
                    error_line: mermaidError.error_line || 0
                };

                console.log(`Retrying mermaid rendering (${retryCount + 1}/${MAX_RETRIES})...`);

                // Wait a short delay before retrying
                setTimeout(() => {
                    init_project_analysis(uuid, retryCount + 1, errorInfo);
                }, 1000);
            } else {
                console.error(`Failed to render mermaid diagram after ${MAX_RETRIES} attempts`);
                // Keep the last attempt's content visible to the user
            }
        }

    } catch (error) {
        console.error('Error initializing project analysis:', error);

        // Remove loading message if it exists
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            chat.removeChild(loadingElement);
        }

        // Show error message
        create_message(`❌ Error al inicializar el análisis del proyecto: ${error.message}. Puedes intentar enviar un mensaje manualmente para continuar.`, false);
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

// Event listeners
input_text.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        send_message();
    }
});

document.getElementById('send-message').addEventListener('click', send_message);

new_chat_btn.addEventListener("click", () => {
    showCreateProjectModal();
});

saveProjectBtn.addEventListener('click', saveProject);

document.addEventListener("DOMContentLoaded", function () {
    initializeDropdown();
    get_projects();
    check_url_for_project();
});