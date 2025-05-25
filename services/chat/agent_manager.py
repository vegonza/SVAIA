from tide_swarm import Agent

from .cve_parser import search_cve
from .prompts import (ANALYSIS_AGENT_PROMPT, CVE_AGENT_PROMPT,
                      MERMAID_AGENT_PROMPT)

cve_agent = Agent(
    name="cve_agent",
    instructions=CVE_AGENT_PROMPT,
    model="openai/gpt-4.1-mini",
    functions=[search_cve],
    tool_choice="auto",
    parallel_tool_calls=False,
)

mermaid_agent = Agent(
    name="mermaid_agent",
    instructions=MERMAID_AGENT_PROMPT,
    model="google/gemini-2.5-flash-preview-05-20",
    tool_choice="none",
    parallel_tool_calls=False,
)

analysis_agent = Agent(
    name="analysis_agent",
    instructions=ANALYSIS_AGENT_PROMPT,
    model="openai/gpt-4.1-mini",
    functions=[search_cve],
    tool_choice="auto",
    parallel_tool_calls=False,
)
