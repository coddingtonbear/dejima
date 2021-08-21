import argparse
import sys

from rich.console import Console

from .exceptions import DejimaError
from .exceptions import DejimaUserError
from .plugin import get_installed_commands


def main(argv=sys.argv):
    commands = get_installed_commands()

    parser = argparse.ArgumentParser()
    parser.add_argument("--debugger", action="store_true")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    for cmd_name, cmd_class in commands.items():
        parser_kwargs = {}

        cmd_help = cmd_class.get_help()
        if cmd_help:
            parser_kwargs["help"] = cmd_help

        subparser = subparsers.add_parser(cmd_name, **parser_kwargs)
        cmd_class.add_arguments(subparser)

    args = parser.parse_args(argv[1:])
    console = Console()

    if args.debugger:
        import debugpy

        debugpy.listen(("0.0.0.0", 5678))
        console.print("[red][italic]Awaiting debugger connection...[/italic][/red]")
        debugpy.wait_for_client()

    try:
        commands[args.command](args, console).handle()
    except DejimaError as e:
        console.print(f"[red]{e}[/red]")
    except DejimaUserError as e:
        console.print(f"[yellow]{e}[/yellow]")
    except Exception:
        console.print_exception(show_locals=True)
