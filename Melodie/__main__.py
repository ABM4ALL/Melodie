import argparse

from MelodieInfra import MelodieExceptions

parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    help="""[action] for starting the management server;
""",
)


def check_args(action: str):
    if action not in {"studio", "info"}:
        raise MelodieExceptions.Program.Variable.VariableNotInSet(
            "Command-Line argument 'action'", action, {"studio"}
        )


args = parser.parse_args()
check_args(args.action)
if args.action == "studio":
    from MelodieStudio.main import studio_main

    studio_main()
elif args.action == "info":
    from Melodie import get_system_info

    get_system_info()
