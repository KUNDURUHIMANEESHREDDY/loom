import asyncio
import sys
import io

# Ensure UTF-8 output encoding on Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from core.engine import AgnoEngine

def print_res(res):
    print("\n🔍 Internal Pipeline Execution & Thoughts")
    for t in res.thoughts:
        print(f"  {t}")
    print(f"\nAgno:\n{res.answer}")
    print(f"\nExecution Time: {res.execution_time_ms}ms | Provider: {res.provider_used}\n")

async def main():
    engine = AgnoEngine()

    print("\n" + "="*80)
    print("DEMO 1: Playlist Pipeline with YouTube oEmbed Normalization & Transcripts")
    print("="*80)
    res1 = await engine.process_query("create a playlist about creating AI agents")
    print_res(res1)

    print("\n" + "="*80)
    print("DEMO 2: PDF Export of Previous Playlist Artifact")
    print("="*80)
    res2 = await engine.process_query("make it pdf")
    print_res(res2)

    print("\n" + "="*80)
    print("DEMO 3: NewsDigestPipeline with Grounded Article Sources")
    print("="*80)
    res3 = await engine.process_query("latest news on mcp")
    print_res(res3)

if __name__ == "__main__":
    asyncio.run(main())
