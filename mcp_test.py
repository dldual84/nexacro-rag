import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(session, tool_name, arguments):
    print()
    print("=" * 80)
    print(f"TOOL: {tool_name}")
    print("=" * 80)
    print(f"입력: {arguments}")
    print()

    result = await session.call_tool(
        tool_name,
        arguments,
    )

    if result.is_error:
        print("❌ Tool 실행 오류")
        print(result)
        return

    print("✅ Tool 실행 성공")
    print()

    if result.structured_content:
        content = result.structured_content

        print(f"검색 결과: {len(content.get('result', []))}건")
        print()

        for index, item in enumerate(
            content.get("result", []),
            start=1,
        ):
            metadata = item.get("metadata", {})

            print(f"[{index}]")
            print(f"source  : {metadata.get('source')}")
            print(f"section : {metadata.get('section')}")
            print(f"title   : {metadata.get('title')}")
            print(f"pages   : {metadata.get('pages')}")

            if "api_intent" in item:
                print(f"api_intent : {item['api_intent']}")

            if "has_code" in item:
                print(f"has_code   : {item['has_code']}")

            print()
            print("내용:")
            print(item.get("text", "")[:1500])
            print()
            print("-" * 80)

    else:
        print(result)


async def main():

    server_params = StdioServerParameters(
        command="mcp",
        args=[
            "run",
            "mcp_server/server.py",
        ],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("=" * 80)
            print("NEXACRO MCP TEST")
            print("=" * 80)

            # --------------------------------------------------
            # MCP Tool 목록
            # --------------------------------------------------

            tools = await session.list_tools()

            print()
            print("등록된 MCP Tools")
            print("-" * 80)

            for tool in tools.tools:
                print(f"- {tool.name}")
                print(f"  {tool.description}")
                print()

            # --------------------------------------------------
            # 1. 일반 검색
            # --------------------------------------------------

            await call_tool(
                session,
                "nexacro_search",
                {
                    "query": "Grid 컴포넌트의 주요 기능",
                    "top_k": 3,
                },
            )

            # --------------------------------------------------
            # 2. API 검색
            # --------------------------------------------------

            await call_tool(
                session,
                "nexacro_api_search",
                {
                    "query": "Grid setCellProperty 메서드 사용법",
                    "top_k": 3,
                },
            )

            # --------------------------------------------------
            # 3. 예제 검색
            # --------------------------------------------------

            await call_tool(
                session,
                "nexacro_example_search",
                {
                    "query": "Grid setCellProperty 실제 사용 예제",
                    "top_k": 3,
                },
            )


if __name__ == "__main__":
    asyncio.run(main())