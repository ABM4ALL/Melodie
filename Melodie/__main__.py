import argparse

from Melodie.basic import MelodieExceptions

parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    help="""[serve] for starting the management server;
[run] for scanning code(NotImplemented)
""",
)


def check_args(action: str):
    if action not in {"studio"}:
        raise MelodieExceptions.Program.Variable.VariableNotInSet(
            "Command-Line argument 'action'", action, {"studio"}
        )


args = parser.parse_args()
check_args(args.action)
if args.action == "studio":
    from MelodieStudio.main import studio_main

    studio_main()
