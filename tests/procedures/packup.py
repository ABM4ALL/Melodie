# -*- coding:utf-8 -*-
# This data will not auto run in pytest command
# It creates a virtual environment for test the pypi package distribution.


import os
import sys


def get_executable(venv_path: str) -> str:
    if sys.platform.lower().find("windows") != -1:
        executable = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        executable = os.path.join(venv_path, "bin", "python")
    return executable


def venvpackup():
    proj_root = os.path.dirname(os.path.dirname(__file__))
    package = os.path.join(proj_root, "dist", r"Melodie-0.1.tar.gz")
    assert os.path.exists(package)
    venv_path = os.path.join(os.path.dirname(__file__), "venv")

    os.system(f"{sys.executable} -m pip install numpy")
    os.system(f"{sys.executable} -m pip install virtualenv")
    os.system(f"{sys.executable} -m virtualenv {venv_path}")
    executable = get_executable(venv_path)
    os.system(f"{executable} -m pip install {package} --no-binary=:all:")

    os.chdir(os.path.dirname(__file__))
    os.system(
        f'{executable} -c "import Melodie.boost as boost;import Melodie.boost.hello; print(dir(boost));boost.b"'
    )
    # print(proj_root)
    os.chdir(proj_root)


def venv_test():
    venv_path = os.path.join(os.path.dirname(__file__), "venv")
    executable = get_executable(venv_path)
    print(executable)
    assert os.path.exists(executable)
    os.system(f"{executable} -m pip install pytest")
    os.system(f"{executable} -m pytest .")


# def remove


if __name__ == "__main__":
    venvpackup()
    # venv_test()
