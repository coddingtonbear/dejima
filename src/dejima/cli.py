import argparse
import sys

from rich.console import Console
from safdie import SafdieRunner

from .constants import COMMAND_ENTRYPOINT_NAME
from .exceptions import DejimaError
from .exceptions import DejimaUserError
from .plugin import CommandPlugin


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--debugger", action="store_true")
    runner = SafdieRunner(
        COMMAND_ENTRYPOINT_NAME,
        CommandPlugin,
        parser=parser,
    )
    args = runner.parse_args(argv[1:])

    console = Console()

    if args.debugger:
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        console.print("[red][italic]Awaiting debugger connection...[/italic][/red]")
        debugpy.wait_for_client()

    try:
        runner.run_command_for_parsed_args(
            args,
            init_kwargs={
                "console": console,
            },
        )
    except DejimaError as e:
        console.print(f"[red]{e}[/red]")
    except DejimaUserError as e:
        console.print(f"[yellow]{e}[/yellow]")
    except Exception:
        console.print_exception(show_locals=True)
