"""Project 12's MCP server: exposes search_docs as a real MCP tool that
Claude Desktop or Claude Code can connect to directly -- separate from
the live web app's own tool-use loop in rag/answer.py, but backed by the
exact same retrieval code (rag/tools.py's execute_search_docs), so there
is only one place the actual search logic lives.

Uses the mcp 2.x SDK API (FastMCP was renamed to MCPServer in 2.x --
matches the same class Project 6's MCP server used).

Run directly for local testing:
    python mcp_server.py

To connect it to Claude Desktop, add an entry to its MCP config pointing
at this file's absolute path with your venv's python, same pattern as
Project 6's MCP server.
"""

from mcp.server.mcpserver import MCPServer

from rag.tools import VALID_TOPICS, execute_search_docs

mcp = MCPServer("project12-search-docs")


@mcp.tool()
def search_docs(topic: str, query: str) -> str:
    """Search one topic's uploaded documents for excerpts relevant to a query.

    topic must be one of: dwdm_osnr, ethernet, ip, others.
    Returns the most relevant excerpts, each tagged with its source
    filename and page number.
    """
    if topic not in VALID_TOPICS:
        return f"Invalid topic '{topic}'. Must be one of: {', '.join(VALID_TOPICS)}."
    return execute_search_docs(topic, query)


if __name__ == "__main__":
    mcp.run(transport="stdio")
