"""
This script file is only concerned about the system information, and generate the report.

Pasting the generated report onto GitHub issues can be of great convenience.
"""
import os.path
import platform


def is_windows() -> bool:
    return platform.system().lower().find("windows") != -1


def melodie_version() -> str:
    """
    Get the version of Melodie.
    :return:
    """
    try:
        with open(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.txt")
        ) as f:
            return f.read()
    except FileNotFoundError:
        import traceback

        traceback.print_exc()
        return ""


def get_system_info(print_info=True) -> str:
    """
    Get the system info
    :param print_info: Whether the information be directly printed to your console.
    :return:
    """
    import numpy
    import Cython

    info = f"""
    Here is the information for Melodie
    ===================================
    Melodie Version  :  {melodie_version()}
    Python Version   :  {platform.python_version()}
    Python Arch      :  {platform.architecture()}
    Platform Detail  :  {platform.platform()}
    Cython Version   :  {Cython.__version__}
    Numpy Version    :  {numpy.__version__}
    """
    if print_info:
        print(info)
    return info
