import asyncio

from pizzagpt_mcp.db.seed_data import run_seed_or_restore
from pizzagpt_mcp.server import mcp


async def main():
    print("Starting DB seed/restore...")
    # Trigger seeding/restore explicitly. Pass None to parse real CLI args,
    # or provide a list like ["--mode", "seed"] to force behavior.
    run_seed_or_restore(None)
    print("Done.")

    print("Starting MCP-Server...")

    await mcp.run_async(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        log_level="debug"
    )

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
