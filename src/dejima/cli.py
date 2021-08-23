import argparse
import sys
from typing import Any
from typing import Dict
from typing import Iterable

from rich.console import Console
from safdie import SafdieRunner

from .constants import COMMAND_ENTRYPOINT_NAME
from .exceptions import DejimaError
from .exceptions import DejimaUserError
from .plugin import CommandPlugin


class Runner(SafdieRunner):
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--debugger", action="store_true")
        return super().add_arguments(parser)

    def handle(
        self,
        args: argparse.Namespace,
        init_args: Iterable[Any],
        init_kwargs: Dict[str, Any],
        handle_args: Iterable[Any],
        handle_kwargs: Dict[str, Any],
    ) -> Any:
        console = Console()

        if args.debugger:
            import debugpy

            debugpy.listen(("0.0.0.0", 5678))
            console.print("[red][italic]Awaiting debugger connection...[/italic][/red]")
            debugpy.wait_for_client()

        init_kwargs["console"] = console

        return super().handle(args, init_args, init_kwargs, handle_args, handle_kwargs)


def main(argv=sys.argv):
    console = Console()

    try:
        Runner(
            COMMAND_ENTRYPOINT_NAME,
            CommandPlugin,
        ).run()
    except DejimaError as e:
        console.print(f"[red]{e}[/red]")
    except DejimaUserError as e:
        console.print(f"[yellow]{e}[/yellow]")
    except Exception:
        console.print_exception(show_locals=True)
