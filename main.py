import argparse
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import settings
from core.engine import LoomEngine

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.tree import Tree
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False


def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        safe_str = text.encode(sys.stdout.encoding, errors="replace").decode(sys.stdout.encoding)
        print(safe_str)


async def run_interactive(provider: str, model: str, verbose: bool = True):
    engine = LoomEngine(provider=provider, model=model)
    provider_name = engine.llm_client.provider.value.upper()
    model_name = engine.llm_client.model

    if HAS_RICH:
        console.print(
            Panel.fit(
                f"[bold cyan]Welcome to Loom AI Engine[/bold cyan]\n"
                f"[yellow]Active Provider:[/yellow] {provider_name} | [yellow]Model:[/yellow] {model_name}\n"
                f"[dim]Type 'exit', 'quit', or 'q' to end the session.[/dim]"
            )
        )
    else:
        safe_print(f"--- Welcome to Loom AI Engine ---")
        safe_print(f"Active Provider: {provider_name} | Model: {model_name}\n")

    while True:
        try:
            if HAS_RICH:
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
            else:
                user_input = input("\nYou: ")

            cleaned_input = user_input.strip()
            if cleaned_input.lower() in ["exit", "quit", "q"]:
                if HAS_RICH:
                    console.print("[yellow]Exiting Loom Engine. Goodbye![/yellow]")
                else:
                    safe_print("Exiting Loom Engine. Goodbye!")
                break

            if not cleaned_input:
                continue

            if HAS_RICH:
                with console.status(f"[cyan]Loom ({provider_name}) is processing pipeline...[/cyan]"):
                    response = await engine.process_query(cleaned_input)

                # Show internal thought steps / pipeline actions if available
                if response.thoughts:
                    tree = Tree("[dim bold cyan]🔍 Internal Pipeline Execution & Thoughts[/dim bold cyan]")
                    for step in response.thoughts:
                        tree.add(f"[dim]{step}[/dim]")
                    console.print(tree)

                console.print(f"\n[bold magenta]Loom:[/bold magenta] {response.answer}")
                if response.sources:
                    console.print(f"[bold yellow]Sources:[/bold yellow] {', '.join(response.sources)}")
                console.print(
                    f"[dim]Execution Time: {response.execution_time_ms}ms | Provider: {response.provider_used}[/dim]"
                )
            else:
                safe_print("Processing pipeline...")
                response = await engine.process_query(cleaned_input)
                if response.thoughts:
                    safe_print("--- Internal Pipeline Execution ---")
                    for step in response.thoughts:
                        safe_print(f"  * {step}")
                safe_print(f"\nLoom: {response.answer}")
                if response.sources:
                    safe_print(f"Sources: {', '.join(response.sources)}")
                safe_print(f"(Execution Time: {response.execution_time_ms}ms)")

        except (KeyboardInterrupt, EOFError):
            safe_print("\nSession ended.")
            break


def main():
    parser = argparse.ArgumentParser(description="Loom AI Reasoning Agent Engine")
    parser.add_argument(
        "--provider",
        type=str,
        default=settings.llm_provider,
        help="LLM Provider: google, deepseek, groq, ollama, or mock",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model name",
    )
    args = parser.parse_args()

    asyncio.run(run_interactive(provider=args.provider, model=args.model))


if __name__ == "__main__":
    main()
