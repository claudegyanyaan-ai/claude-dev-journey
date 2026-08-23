from mcp.server.mcpserver import MCPServer

import lookups

mcp = MCPServer("dictionary")


@mcp.tool()
def lookup_english(word: str) -> str:
    """Look up the English definition of a single word."""
    data = lookups.fetch_english_definition(word)
    return lookups.format_definition(data)


@mcp.tool()
def translate_to_hindi(word: str) -> str:
    """Translate a single English word into Hindi."""
    data = lookups.fetch_hindi_translation(word)
    return lookups.format_translation(data)


if __name__ == "__main__":
    mcp.run()
