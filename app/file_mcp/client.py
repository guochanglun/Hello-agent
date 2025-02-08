import asyncio

from mcp import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env=None
)


async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(tools)

            await session.call_tool("write_file", {"path": "./test.txt", "content": "哈哈哈哈"})

            content = await session.call_tool("read_file", {"path": "./test.txt", "content": ""})
            print(content)


if __name__ == '__main__':
    asyncio.run(run())
