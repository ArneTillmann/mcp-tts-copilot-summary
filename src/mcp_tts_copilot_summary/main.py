from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import register_tools


def create_server() -> FastMCP:
    server = FastMCP("mcp-tts-copilot-summary")
    register_tools(server)
    return server


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
