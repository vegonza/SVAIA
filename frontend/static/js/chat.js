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
let analyzing_project = false;  // New flag to track if project analysis is ongoing

// Initialize mermaid with beautiful configuration
if (window.mermaid) {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        securityLevel: 'loose',
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        logLevel: 'error',
        themeVariables: {
            // Enhanced color palette
            primaryColor: '#4f46e5',
            primaryTextColor: '#1f2937',
            primaryBorderColor: '#6366f1',
            lineColor: '#6b7280',
            secondaryColor: '#f3f4f6',
            tertiaryColor: '#e5e7eb',
            background: '#ffffff',
            mainBkg: '#ffffff',
            secondBkg: '#f8fafc',
            tertiaryBkg: '#f1f5f9'
        },
        flowchart: {
            htmlLabels: true,
            curve: 'basis',
            useMaxWidth: false,
            diagramPadding: 20,
            nodeSpacing: 50,
            rankSpacing: 80,
            padding: 15
        },
        er: { useMaxWidth: false },
        sequence: { useMaxWidth: false, wrap: true, diagramMarginX: 50, diagramMarginY: 10 },
        gantt: { useMaxWidth: false }
    });
}

// Add beautiful CSS animations for mermaid diagrams
function addMermaidAnimations() {
    if (document.getElementById('mermaid-animations')) return;

    const style = document.createElement('style');
    style.id = 'mermaid-animations';
    style.textContent = `
        @keyframes fadeInScale {
            0% {
                opacity: 0;
                transform: scale(0.9) translateY(10px);
            }
            100% {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        .beautiful-mermaid {
            margin: 20px 0;
            border-radius: 16px;
            overflow: hidden;
            position: relative;
            cursor: pointer;
        }

        .mermaid-diagram svg {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .mermaid-diagram:hover svg {
            cursor: pointer;
        }

        /* Enhanced subgraph styling */
        .beautiful-mermaid svg g.cluster rect {
            fill: rgba(248, 250, 252, 0.8) !important;
            stroke: #e2e8f0 !important;
            stroke-width: 2px !important;
            rx: 8 !important;
            ry: 8 !important;
            filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.05)) !important;
        }

        .beautiful-mermaid svg g.cluster text {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            fill: #374151 !important;
        }

        /* Modal animations */
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        @keyframes fadeOut {
            0% { opacity: 1; }
            100% { opacity: 0; }
        }

        @keyframes modalSlideIn {
            0% { 
                opacity: 0;
                transform: scale(0.8) translateY(50px);
            }
            100% { 
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        @keyframes modalSlideOut {
            0% { 
                opacity: 1;
                transform: scale(1) translateY(0);
            }
            100% { 
                opacity: 0;
                transform: scale(0.8) translateY(50px);
            }
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .beautiful-mermaid svg {
                max-width: 100%;
                height: auto;
            }
        }
    `;
    document.head.appendChild(style);
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

        solvabilityDropdown.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            solvabilityDropdownContainer.classList.toggle('show');
        });

        solvabilityOptions.forEach(option => {
            option.addEventListener('click', function (e) {
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
        .replace(/-->-/g, '---') // Fix invalid -->- syntax (should be --- for port connections)
        // Protect --- temporarily, fix --, then restore ---
        .replace(/---/g, '___TRIPLE_DASH___') // Temporarily protect triple dashes
        .replace(/--(?!\>)/g, '-->') // Replace -- with --> when not followed by >
        .replace(/___TRIPLE_DASH___/g, '---') // Restore protected triple dashes
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

/**
 * Enhances the rendered mermaid diagram with beautiful styling
 */
function enhanceMermaidDiagram(container) {
    const svg = container.querySelector('svg');
    if (!svg) return;

    // Add beautiful styling to the SVG
    svg.style.cssText += `
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1), 0 6px 10px rgba(0, 0, 0, 0.05);
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        padding: 20px;
        margin: 20px 0;
        max-width: 100%;
        transition: all 0.3s ease;
    `;

    // Add hover effect
    svg.addEventListener('mouseenter', () => {
        svg.style.transform = 'scale(1.02)';
        svg.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15), 0 10px 20px rgba(0, 0, 0, 0.1)';
    });

    svg.addEventListener('mouseleave', () => {
        svg.style.transform = 'scale(1)';
        svg.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1), 0 6px 10px rgba(0, 0, 0, 0.05)';
    });

    // Enhanced node styling based on classes
    const nodes = svg.querySelectorAll('g.node');
    nodes.forEach(node => {
        const rect = node.querySelector('rect, polygon, circle, ellipse');
        if (rect) {
            // Add gradient backgrounds and better borders
            const classList = node.getAttribute('class') || '';

            if (classList.includes('exposed_port')) {
                rect.style.fill = 'url(#portGradient)';
                rect.style.stroke = '#8b5cf6';
                rect.style.strokeWidth = '2px';
                rect.style.filter = 'drop-shadow(0 2px 4px rgba(139, 92, 246, 0.2))';
            } else if (classList.includes('network')) {
                rect.style.fill = 'url(#networkGradient)';
                rect.style.stroke = '#f59e0b';
                rect.style.strokeWidth = '2px';
                rect.style.filter = 'drop-shadow(0 2px 4px rgba(245, 158, 11, 0.2))';
            } else {
                // Default service styling
                rect.style.fill = 'url(#serviceGradient)';
                rect.style.stroke = '#3b82f6';
                rect.style.strokeWidth = '2px';
                rect.style.filter = 'drop-shadow(0 2px 4px rgba(59, 130, 246, 0.2))';
            }
        }

        // Enhanced text styling
        const text = node.querySelector('text');
        if (text) {
            text.style.fontFamily = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            text.style.fontWeight = '600';
            text.style.fontSize = '14px';
        }
    });

    // Add beautiful gradients
    addGradientDefinitions(svg);

    // Enhanced edge styling
    const edges = svg.querySelectorAll('g.edgePath path');
    edges.forEach(edge => {
        edge.style.stroke = '#6b7280';
        edge.style.strokeWidth = '2px';
        edge.style.filter = 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))';
    });

    // Enhanced arrowheads
    const markers = svg.querySelectorAll('marker polygon');
    markers.forEach(marker => {
        marker.style.fill = '#6b7280';
        marker.style.filter = 'drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))';
    });

    // Add subtle animation to the entire diagram
    svg.style.animation = 'fadeInScale 0.6s ease-out';

    // Add click functionality to expand/view diagram
    container.addEventListener('click', (e) => {
        e.preventDefault();
        openMermaidModal(svg, container);
    });

    // Add visual feedback for clickability
    container.style.cursor = 'pointer';
    container.title = 'Click to view diagram in full screen';
}

/**
 * Opens a modal to display the mermaid diagram in full screen
 */
function openMermaidModal(svg, container) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(8px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        box-sizing: border-box;
        animation: fadeIn 0.3s ease-out;
    `;

    // Create modal content container
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 16px;
        padding: 30px;
        max-width: 95vw;
        max-height: 95vh;
        overflow: auto;
        position: relative;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
        animation: modalSlideIn 0.3s ease-out;
    `;

    // Create close button
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '✕';
    closeButton.style.cssText = `
        position: absolute;
        top: 15px;
        right: 15px;
        background: #f3f4f6;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        color: #6b7280;
        transition: all 0.2s ease;
        z-index: 1;
    `;

    closeButton.addEventListener('mouseenter', () => {
        closeButton.style.background = '#ef4444';
        closeButton.style.color = 'white';
        closeButton.style.transform = 'scale(1.1)';
    });

    closeButton.addEventListener('mouseleave', () => {
        closeButton.style.background = '#f3f4f6';
        closeButton.style.color = '#6b7280';
        closeButton.style.transform = 'scale(1)';
    });

    // Clone the SVG for the modal
    const clonedSvg = svg.cloneNode(true);
    clonedSvg.style.cssText = `
        max-width: 100%;
        max-height: calc(95vh - 100px);
        width: auto;
        height: auto;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
    `;

    // Add title
    const title = document.createElement('h3');
    title.textContent = 'Docker Architecture Diagram';
    title.style.cssText = `
        margin: 0 0 20px 0;
        color: #1f2937;
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        padding-right: 50px;
    `;

    // Assemble modal
    modalContent.appendChild(closeButton);
    modalContent.appendChild(title);
    modalContent.appendChild(clonedSvg);
    modal.appendChild(modalContent);

    // Close modal functionality
    const closeModal = () => {
        modal.style.animation = 'fadeOut 0.3s ease-out';
        modalContent.style.animation = 'modalSlideOut 0.3s ease-out';
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    };

    closeButton.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);

    // Add modal to page
    document.body.appendChild(modal);
}

/**
 * Adds gradient definitions to the SVG for beautiful backgrounds
 */
function addGradientDefinitions(svg) {
    let defs = svg.querySelector('defs');
    if (!defs) {
        defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        svg.insertBefore(defs, svg.firstChild);
    }

    const gradients = [
        {
            id: 'serviceGradient',
            colors: [
                { offset: '0%', color: '#dbeafe', opacity: '1' },
                { offset: '100%', color: '#bfdbfe', opacity: '1' }
            ]
        },
        {
            id: 'portGradient',
            colors: [
                { offset: '0%', color: '#f3e8ff', opacity: '1' },
                { offset: '100%', color: '#e9d5ff', opacity: '1' }
            ]
        },
        {
            id: 'networkGradient',
            colors: [
                { offset: '0%', color: '#fef3c7', opacity: '1' },
                { offset: '100%', color: '#fde68a', opacity: '1' }
            ]
        }
    ];

    gradients.forEach(gradientData => {
        if (!svg.querySelector(`#${gradientData.id}`)) {
            const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
            gradient.setAttribute('id', gradientData.id);
            gradient.setAttribute('x1', '0%');
            gradient.setAttribute('y1', '0%');
            gradient.setAttribute('x2', '100%');
            gradient.setAttribute('y2', '100%');

            gradientData.colors.forEach(colorData => {
                const stop = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
                stop.setAttribute('offset', colorData.offset);
                stop.setAttribute('stop-color', colorData.color);
                stop.setAttribute('stop-opacity', colorData.opacity);
                gradient.appendChild(stop);
            });

            defs.appendChild(gradient);
        }
    });
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
                diagramDiv.className = 'mermaid-diagram beautiful-mermaid';

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
                                        enhanceMermaidDiagram(diagramDiv);
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
    if (loading || !current_project_uuid || analyzing_project) {
        // Show a message to user if trying to send during analysis
        if (analyzing_project) {
            show_warning("Por favor, espere a que termine el análisis del proyecto antes de enviar mensajes.");
        }
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

        // Ensure the message div has the proper styling from the start
        if (!message_div.classList.contains('bg-secondary')) {
            message_div.classList.add('bg-secondary', 'text-white');
        }

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

                                // Parse final markdown without cursor and render mermaid diagrams
                                parseMarkdownIncremental(full_content, content_div, false);

                                // Render mermaid diagrams in the final content
                                render_mermaid_diagrams(content_div).catch(mermaidError => {
                                    console.error('Error rendering mermaid diagrams:', mermaidError);
                                });
                            }
                            break;
                        }

                        if (data.type === 'text' && data.content) {
                            full_content += data.content;
                            is_in_tool_call = false;

                            if (content_div) {
                                // Parse markdown incrementally as content arrives
                                parseMarkdownIncremental(full_content, content_div, true);
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

    const existingVulnerability = project.max_vulnerability_level || '';
    if (existingVulnerability) {
        const predefinedValues = {
            'critical': 'Grado de vulnerabilidad crítico',
            'severe': 'Grado de vulnerabilidad severa',
            'mild': 'Grado de vulnerabilidad leve o medio'
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
            // Update existing project using FormData
            const formData = new FormData();
            formData.append('name', name);
            formData.append('description', description);
            formData.append('max_vulnerability_level', vulnerabilityLevel);
            
            if (totalVulnerabilities !== null) {
                formData.append('total_vulnerabilities_criteria', totalVulnerabilities);
            }
            
            if (solvabilityCriteria) {
                formData.append('solvability_criteria', solvabilityCriteria);
            }
            
            // Add files if any are selected
            if (dockerfilesInput.files.length > 0) {
                for (let file of dockerfilesInput.files) {
                    formData.append('dockerfiles', file);
                }
            }
            
            if (dockerComposeFilesInput.files.length > 0) {
                for (let file of dockerComposeFilesInput.files) {
                    formData.append('docker_compose_files', file);
                }
            }
            
            if (dockerImagesInput.files.length > 0) {
                for (let file of dockerImagesInput.files) {
                    formData.append('images', file);
                }
            }

            response = await fetch(`/sql/projects/${uuid}`, {
                method: 'PUT',
                body: formData
            });
        } else {
            // Create new project using FormData
            const formData = new FormData();
            formData.append('name', name);
            formData.append('description', description);
            formData.append('max_vulnerability_level', vulnerabilityLevel);
            
            if (totalVulnerabilities !== null) {
                formData.append('total_vulnerabilities_criteria', totalVulnerabilities);
            }
            
            if (solvabilityCriteria) {
                formData.append('solvability_criteria', solvabilityCriteria);
            }
            
            // Add files if any are selected
            if (dockerfilesInput.files.length > 0) {
                for (let file of dockerfilesInput.files) {
                    formData.append('dockerfiles', file);
                }
            }
            
            if (dockerComposeFilesInput.files.length > 0) {
                for (let file of dockerComposeFilesInput.files) {
                    formData.append('docker_compose_files', file);
                }
            }
            
            if (dockerImagesInput.files.length > 0) {
                for (let file of dockerImagesInput.files) {
                    formData.append('images', file);
                }
            }

            response = await fetch("/sql/projects", {
                method: 'POST',
                body: formData
            });
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Error desconocido' }));
            throw new Error(errorData.error || `Error al guardar el proyecto: ${response.status}`);
        }

        data = await response.json();

        projectModal.hide();
        await get_projects();

        if (!isEditMode) {
            load_project(data.uuid);
            // Initialize project analysis if files were uploaded
            const hasFiles = dockerfilesInput.files.length > 0 ||
                dockerComposeFilesInput.files.length > 0 ||
                dockerImagesInput.files.length > 0;
            
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

    // Reset analysis state when switching projects
    analyzing_project = false;
    updateInputState();

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

async function init_project_analysis(uuid, retryCount = 0) {
    if (!uuid) return;

    // Set analysis flag to prevent user input
    analyzing_project = true;
    updateInputState();

    // Max retries for mermaid rendering
    const MAX_RETRIES = 3;

    try {
        // Phase 1: Initialize project and generate mermaid diagram
        console.log('Starting Phase 1: Mermaid diagram generation');
        await execute_init_project_phase(uuid, retryCount);

        // Phase 2: Analyze project vulnerabilities
        console.log('Starting Phase 2: Vulnerability analysis');
        await execute_analyze_project_phase(uuid);

    } catch (error) {
        console.error('Error during project analysis:', error);

        // Show error message without retry option
        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.innerHTML = `
            <li class="d-flex align-items-start mb-3 container-fluid pe-0">
                <i class="bi bi-robot me-4"></i>
                <div class="bg-danger text-white p-4 rounded-2 container-fluid">
                    <h6><i class="bi bi-exclamation-triangle"></i> Error en el Análisis del Proyecto</h6>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <div class="mt-3">
                        <small class="text-light d-block">
                            El análisis automático falló. Puedes enviar mensajes manualmente para continuar interactuando con el proyecto.
                        </small>
                    </div>
                </div>
            </li>
        `;

        chat.appendChild(errorMessageDiv);
        chat.scrollTop = chat.scrollHeight;
    } finally {
        // Always re-enable input after analysis completes or fails
        analyzing_project = false;
        updateInputState();
        console.log('Project analysis completed, user input enabled');
    }
}

async function execute_init_project_phase(uuid, retryCount = 0) {
    const MAX_RETRIES = 3;
    const loadingId = `loading-init-${Date.now()}`;

    // Show loading message for Phase 1
    const loadingMessage = document.createElement("div");
    loadingMessage.id = loadingId;
    loadingMessage.innerHTML = `
        <li class="d-flex align-items-start mb-3 container-fluid pe-0">
            <i class="bi bi-robot me-4"></i>
            <div class="bg-primary text-white p-4 rounded-2 container-fluid">
                <div class="d-flex align-items-center">
                    <div class="spinner-border text-light me-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span>${retryCount > 0 ? `Reintentando generación de diagrama (${retryCount}/${MAX_RETRIES})...` : 'Fase 1: Generando diagrama de arquitectura...'}</span>
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
    }

    chat.appendChild(loadingMessage);
    chat.scrollTop = chat.scrollHeight;

    const response = await fetch('/chat/init-project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ project_uuid: uuid })
    });

    if (!response.ok) {
        // Remove loading message before throwing error
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            chat.removeChild(loadingElement);
        }
        throw new Error(`Fase 1 falló - Server responded with ${response.status}: ${response.statusText}`);
    }

    // Process the response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let finalContent = '';

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n\n');

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

    // Try to render mermaid diagrams
    try {
        await render_mermaid_diagrams(contentDiv);
        console.log('Successfully rendered all mermaid diagrams in Phase 1');
    } catch (mermaidError) {
        console.error('Error rendering mermaid diagram:', mermaidError);

        // If we haven't reached max retries, try again
        if (retryCount < MAX_RETRIES - 1) {
            // Remove the message that failed rendering
            chat.removeChild(messageElement);

            console.log(`Retrying mermaid rendering (${retryCount + 1}/${MAX_RETRIES})...`);

            // Wait a short delay before retrying
            setTimeout(() => {
                execute_init_project_phase(uuid, retryCount + 1);
            }, 1000);
            return; // Exit early, retry will handle the rest
        } else {
            console.error(`Failed to render mermaid diagram after ${MAX_RETRIES} attempts`);
            // Keep the last attempt's content visible to the user
        }
    }
}

async function execute_analyze_project_phase(uuid) {
    const loadingId = `loading-analyze-${Date.now()}`;

    // Show loading message for Phase 2
    const loadingMessage = document.createElement("div");
    loadingMessage.id = loadingId;
    loadingMessage.innerHTML = `
        <li class="d-flex align-items-start mb-3 container-fluid pe-0">
            <i class="bi bi-robot me-4"></i>
            <div class="bg-warning text-dark p-4 rounded-2 container-fluid">
                <div class="d-flex align-items-center">
                    <div class="spinner-border text-dark me-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span>Fase 2: Analizando vulnerabilidades del proyecto...</span>
                </div>
            </div>
        </li>
    `;

    chat.appendChild(loadingMessage);
    chat.scrollTop = chat.scrollHeight;

    const response = await fetch('/chat/analyze-project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ project_uuid: uuid })
    });

    if (!response.ok) {
        // Remove loading message before throwing error
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            chat.removeChild(loadingElement);
        }
        throw new Error(`Fase 2 falló - Server responded with ${response.status}: ${response.statusText}`);
    }

    // Remove the loading message
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        chat.removeChild(loadingElement);
    }

    // Stream the analysis response
    const response_id = message_counter++;
    const placeholder = document.createElement("div");
    placeholder.id = `message-${response_id}`;

    const template = ai_template.content.cloneNode(true);
    const message_div = template.querySelector(".message-content");
    message_div.id = `content-${response_id}`;

    // Ensure the message div has the proper styling from the start
    if (!message_div.classList.contains('bg-secondary')) {
        message_div.classList.add('bg-secondary', 'text-white');
    }

    placeholder.appendChild(template);
    chat.appendChild(placeholder);
    chat.scrollTop = chat.scrollHeight;

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

                            // Parse final markdown without cursor and render mermaid diagrams
                            parseMarkdownIncremental(full_content, content_div, false);

                            // Render mermaid diagrams in the final content
                            render_mermaid_diagrams(content_div).catch(mermaidError => {
                                console.error('Error rendering mermaid diagrams:', mermaidError);
                            });
                        }
                        break;
                    }

                    if (data.type === 'text' && data.content) {
                        full_content += data.content;
                        is_in_tool_call = false;

                        if (content_div) {
                            // Parse markdown incrementally as content arrives
                            parseMarkdownIncremental(full_content, content_div, true);
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
                                    <span>Buscando información de CVE: <strong>${data.tool_name}</strong></span>
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

    console.log('Phase 2 completed: Vulnerability analysis finished');

    // Show completion message
    const completionMessageDiv = document.createElement("div");
    completionMessageDiv.innerHTML = `
        <li class="d-flex align-items-start mb-3 container-fluid pe-0">
            <i class="bi bi-robot me-4"></i>
            <div class="bg-success text-white p-4 rounded-2 container-fluid">
                <div class="d-flex align-items-center">
                    <i class="bi bi-check-circle me-3 fs-5"></i>
                    <span><strong>Análisis Completado</strong> - Ahora puedes enviar mensajes para hacer preguntas sobre el proyecto y sus vulnerabilidades.</span>
                </div>
            </div>
        </li>
    `;

    chat.appendChild(completionMessageDiv);
    chat.scrollTop = chat.scrollHeight;
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

// Helper function to safely parse markdown incrementally
function parseMarkdownSafely(content, contentDiv) {
    try {
        if (window.marked && content.trim()) {
            marked.setOptions({
                breaks: true,
                tables: true,
                smartLists: true,
                sanitize: false,
                gfm: true,
                highlight: function (code, lang) {
                    if (lang === 'mermaid') {
                        return code;
                    }
                    return code;
                }
            });

            // Clean up the content before parsing
            const cleanContent = content
                .replace(/\r\n/g, '\n')
                .replace(/\r/g, '\n');

            contentDiv.innerHTML = marked.parse(cleanContent);

            // Render mermaid diagrams in the final content
            render_mermaid_diagrams(contentDiv).catch(mermaidError => {
                console.error('Mermaid rendering error:', mermaidError);
            });
        } else {
            contentDiv.textContent = content;
        }
    } catch (error) {
        console.error('Error parsing markdown:', error);
        // Fallback to simple text with line breaks
        contentDiv.innerHTML = content.replace(/\n/g, '<br>');
    }
}

// Helper function for incremental markdown parsing during streaming
function parseMarkdownIncremental(content, contentDiv, showCursor = true) {
    try {
        if (window.marked && content.trim()) {
            marked.setOptions({
                breaks: true,
                tables: true,
                smartLists: true,
                sanitize: false,
                gfm: true,
                highlight: function (code, lang) {
                    if (lang === 'mermaid') {
                        return code;
                    }
                    return code;
                }
            });

            // Clean up the content before parsing
            const cleanContent = content
                .replace(/\r\n/g, '\n')
                .replace(/\r/g, '\n');

            // Try to parse as markdown
            const parsedContent = marked.parse(cleanContent);
            contentDiv.innerHTML = parsedContent + (showCursor ? "<span class='typing-cursor'>▋</span>" : "");
        } else {
            // Fallback to simple text replacement
            const displayContent = content.replace(/\n/g, '<br>');
            contentDiv.innerHTML = displayContent + (showCursor ? "<span class='typing-cursor'>▋</span>" : "");
        }
    } catch (error) {
        // If markdown parsing fails, fall back to simple text replacement
        console.warn('Incremental markdown parsing failed, using fallback:', error);
        const displayContent = content.replace(/\n/g, '<br>');
        contentDiv.innerHTML = displayContent + (showCursor ? "<span class='typing-cursor'>▋</span>" : "");
    }
}

// Function to update input state based on analysis status
function updateInputState() {
    const sendButton = document.getElementById('send-message');

    if (analyzing_project) {
        input_text.disabled = true;
        input_text.placeholder = "Analizando proyecto... Por favor espere.";
        sendButton.disabled = true;
        sendButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Analizando...';
    } else {
        input_text.disabled = false;
        input_text.placeholder = "Escribe tu mensaje...";
        sendButton.disabled = false;
        sendButton.innerHTML = 'Enviar';
    }
}

// Event listeners
input_text.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !analyzing_project) {
        send_message();
    }
});

document.getElementById('send-message').addEventListener('click', () => {
    if (!analyzing_project) {
        send_message();
    }
});

new_chat_btn.addEventListener("click", () => {
    showCreateProjectModal();
});

saveProjectBtn.addEventListener('click', saveProject);

document.addEventListener("DOMContentLoaded", function () {
    addMermaidAnimations();
    initializeDropdown();
    updateInputState(); // Initialize input state
    get_projects();
    check_url_for_project();
});