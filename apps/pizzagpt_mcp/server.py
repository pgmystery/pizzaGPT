from fastmcp import FastMCP
# from mcp.types import Icon


mcp = FastMCP(
    name="PizzaGPT MCP Server",
    instructions="MCP tools for menu, orders, and customers for an AI pizza restaurant.",
    host="0.0.0.0",
    port=8000,
    # icons=[
    #     Icon(
    #         src="",
    #         mimeType="image/png",
    #         sizes=["48x48"]
    #     ),
    # ],
)


from pizzagpt_mcp.tools import * # type: ignore
from pizzagpt_mcp.api import * # type: ignore
