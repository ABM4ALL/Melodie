import argparse

from MelodieInfra import MelodieExceptions

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
subparser_static_check = subparsers.add_parser("check", help="Melodie Static checker")
subparser_static_check.add_argument("-d", help="Directory to check")

subparser_studio = subparsers.add_parser("studio", help="Start MelodieStudio")
subparser_info = subparsers.add_parser("info", help="Show Information of Melodie")


def handle_check(args):
    from MelodieInfra.static_analysis import StaticCheckerRoutine

    StaticCheckerRoutine(args.d).run()


def handle_studio(args):
    from MelodieStudio.main import studio_main

    studio_main()


def handle_info(args):
    from Melodie import get_system_info

    get_system_info()


subparser_static_check.set_defaults(func=handle_check)
subparser_studio.set_defaults(func=handle_studio)
subparser_info.set_defaults(func=handle_info)


args = parser.parse_args()
args.func(args)
