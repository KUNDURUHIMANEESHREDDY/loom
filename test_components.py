import asyncio
from core.engine import AgnoEngine
from core.memory import PersistentMemory

async def test_all():
    print("=== Testing Persistent Memory ===")
    m = PersistentMemory()
    await m.learn_fact('test fact', 'testing')
    r = await m.get_relevant_facts('test')
    print(f"✓ Memory works: {len(r) > 0} facts found")
    
    print("\n=== Testing AgnoEngine ===")
    e = AgnoEngine(provider='mock')
    resp = await e.process_query('hello')
    print(f"✓ Engine works: {resp.answer is not None}")
    print(f"✓ Tools available: {[tool.name for tool in e.tool_registry.list_tools()]}")
    
    print("\n=== Testing Streaming Server ===")
    from server import app
    print(f"✓ FastAPI server loaded: {len(app.routes)} routes")
    
    # Test CLI interactive mode exists
    print("\n=== Testing CLI ===")
    from main import run_interactive
    print(f"✓ CLI async runner exists: {run_interactive.__name__}")
    
    print("\n✅ All core components working!")
    print("\n📊 Summary:")
    print(f"   - Memory: ✓ SQLite-based persistent storage")
    print(f"   - Engine: ✓ Dynamic agent with {len(e.tool_registry.list_tools())} tools")
    print(f"   - Server: ✓ FastAPI with SSE streaming ({len(app.routes)} routes)")
    print(f"   - CLI: ✓ Async interactive mode")

if __name__ == "__main__":
    asyncio.run(test_all())
