import asyncio
import sys
import pytest
from main import safe_print
from core.engine import AgnoEngine


@pytest.mark.asyncio
async def test_main_directly():
    safe_print("=" * 60)
    safe_print("          AGNO AI ENGINE - DIRECT FUNCTIONAL TEST           ")
    safe_print("=" * 60)

    # Initialize AgnoEngine with mock provider for reproducible testing
    engine = AgnoEngine(provider="mock")

    test_queries = [
        "write documentation about LangGraph",
        "create a playlist about AI agents",
        "latest news on artificial intelligence",
        "make it pdf",
        "research LangGraph, summarize key takeaways, and export as pdf",
        "https://www.youtube.com/watch?v=BsWxPI9UM4c take full transcripts organize and make it pdf"
    ]

    for idx, query in enumerate(test_queries, 1):
        safe_print(f"\n[TEST #{idx}] USER QUERY: \"{query}\"")
        safe_print("-" * 50)

        response = await engine.process_query(query)

        safe_print(f"Provider: {response.provider_used} | Execution Time: {response.execution_time_ms} ms")
        if response.thoughts:
            safe_print(f"Internal Pipeline Steps ({len(response.thoughts)}):")
            for t in response.thoughts[:4]:
                safe_print(f"  * {t}")

        safe_print("\nOUTPUT PREVIEW:")
        lines = [line for line in response.answer.split("\n") if line.strip()]
        for line in lines[:6]:
            safe_print(f"  {line}")
        safe_print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_main_directly())
