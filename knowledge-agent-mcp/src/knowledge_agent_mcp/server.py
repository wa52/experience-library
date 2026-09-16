from __future__ import annotations

import anyio
import click
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolRequestParams, ListToolsResult, PaginatedRequestParams

from knowledge_agent_mcp.application import build_application
from knowledge_agent_mcp.mcp_compat import types


def create_server() -> Server:
    app = build_application()
    server = Server(app.settings.server.name)

    @server.list_tools()
    async def handle_list_tools(
        params: PaginatedRequestParams | None = None,
    ) -> ListToolsResult:
        return app.list_tools()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict[str, object]) -> types.CallToolResult:
        return await app.call_tool(name, arguments)

    return server


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio"]),
    default="stdio",
    help="Transport type for the MCP server.",
)
def main(transport: str) -> int:
    server = create_server()

    async def run_stdio() -> None:
        async with stdio_server() as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    anyio.run(run_stdio)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
