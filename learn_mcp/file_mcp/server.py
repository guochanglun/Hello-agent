import asyncio
import logging

from mcp import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("server")

app = Server("file_mcp_server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    # logger.info("list_tools------------------------")
    return [
        Tool(
            name="read_file",
            description="读取文件内容",
            inputSchema={
                "path": "文件绝对路径"
            }
        ),
        Tool(
            name="write_file",
            description="写入文件内容",
            inputSchema={
                "path": "文件绝对路径",
                "content": "文件内容"
            }
        )
    ]


@app.call_tool()
async def call_toos(name: str, arguments: dict) -> list[TextContent] | None:
    # logger.info(f"call_toos------------------------ name: {name}, arguments: {arguments}")
    path = arguments.get("path")
    content = arguments.get("content")
    if name == "read_file":
        file_content = read_file(path)
        return [TextContent(type="text", text=file_content)]

    if name == "write_file":
        write_file(path, content)


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def write_file(path: str, content: str):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


# 启动 MCP服务器
async def main():
    async with stdio_server() as (read_stream, write_stream):
        try:
            # 异步运行 MCP 应用程序
            await app.run(
                read_stream,
                write_stream,
                # 用于初始化应用程序的选项，通常包含配置或上下文信息
                app.create_initialization_options()
            )
        # 捕获运行 app.run() 时发生的所有异常
        except Exception as e:
            raise


if __name__ == "__main__":
    asyncio.run(main())