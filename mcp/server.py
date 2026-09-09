"""
MCP server exposing the existing Nexacro RAG search tools.

The MCP layer is intentionally thin:
it does not replace the existing HybridSearch, Ranking,
or tool implementations.

It only exposes them through Model Context Protocol so that
an MCP-compatible AI host can call the Nexacro RAG tools directly.
"""

from typing import Any

from mcp.server import MCPServer

from tools.nexacro_api_search import NexacroApiSearchTool
from tools.nexacro_example_search import NexacroExampleSearchTool
from tools.nexacro_search import NexacroSearchTool


# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = MCPServer(
    "Nexacro RAG",
    instructions=(
        "Nexacro 17 technical-document search server. "
        "Use the general search tool for concepts and components, "
        "the API search tool for properties, methods, and events, "
        "and the example search tool for implementation examples."
    ),
)


# ---------------------------------------------------------
# Existing Nexacro RAG tools
# ---------------------------------------------------------

_general_tool = NexacroSearchTool()
_api_tool = NexacroApiSearchTool()
_example_tool = NexacroExampleSearchTool()


# ---------------------------------------------------------
# Result normalization
# ---------------------------------------------------------

def _normalize_results(
    results: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Convert internal RAG search results into a compact
    JSON-serializable structure for MCP clients.
    """

    normalized: list[dict[str, Any]] = []

    for result in results:
        metadata = result.get("metadata", {}) or {}

        item: dict[str, Any] = {
            "text": result.get("text", ""),
            "metadata": {
                "source": metadata.get("source", ""),
                "section": metadata.get("section", ""),
                "title": metadata.get("title", ""),
                "pages": metadata.get("pages", ""),
            },
        }

        # Preserve useful ranking / classification information.
        for key in (
            "hybrid_score",
            "score",
            "api_score",
            "api_intent",
            "example_score",
            "final_example_score",
            "has_code",
            "api_syntax_only",
        ):
            if key in result:
                item[key] = result[key]

        normalized.append(item)

    return normalized


# ---------------------------------------------------------
# Tool 1 : General Nexacro Search
# ---------------------------------------------------------

@mcp.tool()
def nexacro_search(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search general Nexacro 17 documentation and
    component information.
    """

    top_k = max(1, min(top_k, 20))

    results = _general_tool.run(
        query=query,
        search_top_k=max(top_k * 4, 10),
        ranking_top_k=top_k,
    )

    return _normalize_results(results)


# ---------------------------------------------------------
# Tool 2 : Nexacro API Search
# ---------------------------------------------------------

@mcp.tool()
def nexacro_api_search(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search Nexacro 17 Property, Method, Event,
    and API documentation.
    """

    top_k = max(1, min(top_k, 20))

    results = _api_tool.run(
        query=query,
        search_top_k=max(top_k * 10, 30),
        ranking_top_k=top_k,
    )

    return _normalize_results(results)


# ---------------------------------------------------------
# Tool 3 : Nexacro Example Search
# ---------------------------------------------------------

@mcp.tool()
def nexacro_example_search(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search Nexacro 17 implementation examples
    and sample code.
    """

    top_k = max(1, min(top_k, 20))

    results = _example_tool.run(
        query=query,
        search_top_k=max(top_k * 10, 30),
        ranking_top_k=top_k,
    )

    return _normalize_results(results)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    # MCP SDK v2 defaults to stdio transport.
    # This is suitable for local MCP hosts.
    mcp.run()
