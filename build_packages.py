import os
import json
import platform
import shutil
import sys
import time
from tempfile import TemporaryDirectory
from typing import Tuple

from package_parser import parse, normalize_name

requirements_filenames = {
    ("windows", "x86"): "build_requirements.txt",
    ("windows", "amd64"): "build_requirements.txt",
    ("darwin", "amd64"): "build_requirements.txt",
    ("darwin", "arm"): "build_requirements.txt",
}

CONDA_ACTIVATION = "source ~/opt/anaconda3/etc/profile.d/conda.sh && " if sys.platform.lower() == 'darwin' else ''
FORCE_REINSTALL = False


def has_built_package(version: str, plat_name: str, arch: str):
    prefix, suffix = {
        ('darwin', 'amd64'): ('macosx', 'x86_64'),
        ('darwin', 'arm'): ('macosx', 'arm64')
    }[(plat_name, arch)]
    assert plat_name in {"windows", "darwin"}
    for package_name in os.listdir("archive"):
        attrs = parse(package_name)
        pyver: str = attrs['pyver']
        version_str = pyver[2:]
        version_str = version_str[0] + "." + version_str[1:]

        plat: str = attrs['plat']
        print(version, version_str, plat.startswith(prefix), plat.endswith(suffix), version == version_str)
        # time.sleep(10)
        if plat.startswith(prefix) and plat.endswith(suffix) and version == version_str:
            return True
    return False


def build_process(os_name, arch, version, conda_name):
    print(f"building package on {os_name} {arch}, version {version}")
    if os.path.exists("build"):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree("dist")
    cmd = (
            CONDA_ACTIVATION +
            f"conda activate {conda_name} && "
            f"python -m pip install -r {requirements_filenames[(os_name, arch)]} -i https://pypi.tuna.tsinghua.edu.cn/simple && "
            f" python setup.py build_ext -i -f && python setup.py bdist_wheel"
    )
    os.system(
        f"{cmd}"
    )
    files = os.listdir('dist')
    assert len(files) == 1
    wheel_file = os.path.join('dist', files[0])
    cmd = (
            CONDA_ACTIVATION + " && " +
            f"conda activate {conda_name} && python -m pip install {wheel_file} "
            f" -i https://pypi.tuna.tsinghua.edu.cn/simple {'--force-reinstall' if FORCE_REINSTALL else ''}"
    )
    os.system(cmd)
    with TemporaryDirectory() as tmpdirname:
        shutil.copytree('tests', f"{tmpdirname}/tests")
        cmd = (
                CONDA_ACTIVATION + " && " +
                f"conda activate {conda_name} && cd {tmpdirname} && python -m pytest"
        )
        ret = os.system(cmd) >> 8
        print(f"package test finished with exit code {ret}")
    shutil.copyfile(wheel_file, os.path.join("archive", os.path.basename(wheel_file)))


def build(d):
    if not os.path.exists('archive'):
        os.mkdir("archive")
    for os_name, os_content in d.items():
        if os_name != platform.system().lower():
            continue
        for interpreter_item in os_content:
            arch, version, conda_name = interpreter_item['arch'], interpreter_item[
                'version'], interpreter_item['conda-name']
            if has_built_package(version, os_name, arch):
                print((version, os_name, arch), "already built, skipping...")
                continue
            args = (os_name, arch, version, conda_name)
            build_process(*args)


if __name__ == "__main__":
    config_file = os.path.join("deployment", "interpreters.json")
    with open(config_file, "r", encoding="utf-8") as f:
        d = json.load(f)
    build(d)
