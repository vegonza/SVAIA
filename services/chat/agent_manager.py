from swarm import Agent

from .cve_parser import search_cve

cve_agent = Agent(
    name="cve_agent",
    instructions="You are a cve agent",
    model="openai/gpt-4.1-nano",
    functions=[search_cve],
    tool_choice="auto",
    parallel_tool_calls=False,
)
