from .types import File


def CVE_AGENT_PROMPT(context_variables: dict) -> str:
    archivos_str = FilesFormat(context_variables["archivos"])

    return """
Eres un asistente útil para una plataforma de ciberseguridad.

# Información del Proyecto
- **Nombre del Proyecto**: {project_name}
- **Descripción**: {project_description}

# Criterios de Aceptabilidad del Proyecto
- **Nivel máximo de vulnerabilidad permitido**: {max_vulnerability_level}
- **Número total máximo de vulnerabilidades**: {total_vulnerabilities_criteria}
- **Criterio de solucionabilidad**: {solvability_criteria}

# Formato de Respuestas
Formatea tus respuestas usando markdown:
- Usa **negrita** para términos importantes
- Usa # para encabezados principales
- Usa ## para subencabezados
- Usa *cursiva* para énfasis
- Usa `código` para fragmentos de código
- Usa listas con viñetas con - o listas numeradas cuando sea apropiado

Mantén tus respuestas concisas e informativas.

El usuario tiene estos archivos:
{archivos}
""".format(**context_variables, archivos=archivos_str)


def MERMAID_AGENT_PROMPT(context_variables: dict) -> str:
    archivos_str = FilesFormat(context_variables["archivos"])

    return f"""
Create a mermaid chart for the docker compose configuration showing:
- All services from the docker-compose.yml
- Ports exposed by each service
- Connections between services
- Networks (if defined)

Follow this structure and use subgraphs to organize the diagram:

```mermaid
graph TD
    subgraph Services
        service1[Service Name]
        service2[Another Service]
    end

    subgraph Exposed Ports
        port1(H-80:C-80)
        port2(H-3000:C-3000)
    end

    subgraph Networks
        network1(network_name)
    end

    %% Connect services to their ports (use exactly --- not -->-)
    service1 --- port1
    service2 --- port2

    %% Service dependencies (depends_on)
    service1 --> service2

    %% Network connections
    service1 -- network1
    service2 -- network1

    %% Implied connections (dotted lines)
    service1 -.-> service2

    %% Color coding
    classDef default fill:#ACE5EE,stroke:#333,stroke-width:2px;
    classDef exposed_port fill:#E5CCFF,stroke:#333,stroke-width:2px;
    classDef network fill:#FFFACD,stroke:#333,stroke-width:2px;
    
    class port1,port2 exposed_port;
    class network1 network;
```

Key elements to use:
- Services: `[Service Name]` (rectangles)
- Ports: `(H-hostport:C-containerport)` (circles) 
- Networks: `(network_name)` (circles)
- Solid arrows `-->` for dependencies
- Dotted arrows `-.->` for implied connections
- Triple dashes `---` for port connections (NOT `-->-`)
- Double dashes `--` for network connections

IMPORTANT: Use exactly `---` (three dashes) for port connections, never `-->-` which causes parse errors.

Port format: Use H-hostport:C-containerport (e.g., H-80:C-80 for host port 80 mapping to container port 80)

Use subgraphs to organize: Services, Exposed Ports, and Networks (if any).

Analyze the docker-compose.yml file and create a comprehensive mermaid diagram following this structure.

El usuario tiene estos archivos:
{archivos_str}
""".strip()


def FilesFormat(archivos: list[File]) -> str:
    return "\n".join([f"Archivo: {archivo['name']}\nContenido: {archivo['content']}" for archivo in archivos])
