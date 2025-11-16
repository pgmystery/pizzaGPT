from starlette.requests import Request
from starlette.responses import JSONResponse

from pizzagpt_mcp.server import mcp


@mcp.custom_route("/tools", methods=["GET"])
async def tools(_: Request) -> JSONResponse:
    response = {}
    tools = await mcp.get_tools()

    for tool in tools:
        response[tool] = tools[tool].description

    return JSONResponse(response)
