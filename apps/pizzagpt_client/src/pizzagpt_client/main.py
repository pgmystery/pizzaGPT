import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


async def main():
    client = MultiServerMCPClient(
        {
            "pizzagpt": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    llm = ChatOllama(
        model="llama3.2:3b",
        validate_model_on_init=True,
        temperature=0,
    )

    tools = await client.get_tools()
    agent = create_agent(
        model=llm,
        tools=tools,
    )
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )


if __name__ == "__main__":
    asyncio.run(main())
