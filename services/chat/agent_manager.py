from swarm import Agent

from .cve_parser import search_cve

cve_agent = Agent(
    name="cve_agent",
    instructions="You are a cve agent",
    model="gemini-2.5-flash-preview-05-20",
    functions=[search_cve]
)
