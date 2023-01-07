import os
import json
import shutil
from tempfile import TemporaryDirectory
requirements_filenames = {
    ("windows", "x86"): "build_requirements.txt",
    ("windows", "amd64"): "build_requirements.txt",
}

def build_process(os_name, arch,version, conda_name):
    print(f"building package on {os_name} {arch}, version {version}")
    if os.path.exists('dist'):
        shutil.rmtree("dist")
    # mkdir("dist")
    cmd = (f"conda activate {conda_name} && "
            f"python -m pip install -r {requirements_filenames[(os_name, arch)]} -i https://pypi.tuna.tsinghua.edu.cn/simple && "
            f"python setup.py bdist_wheel"
            )
    os.system(
        cmd
    )
    files = os.listdir('dist')
    assert len(files) == 1
    wheel_file = os.path.join('dist', files[0])
    cmd = (
        f"conda activate {conda_name} && python -m pip install {wheel_file} -i https://pypi.tuna.tsinghua.edu.cn/simple --force-reinstall"
    )
    os.system(cmd)
    with TemporaryDirectory() as tmpdirname:
        shutil.copytree('tests', f"{tmpdirname}/tests")
        cmd = (
            f"conda activate {conda_name} && cd {tmpdirname} && python -m pytest"
        )
        ret = os.system(cmd) >> 8
        print(f"package test finished with exit code {ret}")
    shutil.copyfile(wheel_file, os.path.join("archive", os.path.basename(wheel_file)))


def build(d):
    if not os.path.exists('archive'):
        os.mkdir("archive")
    for os_name, os_content in d.items():
        for interpreter_item in os_content:
            arch, version,  conda_name = interpreter_item['arch'], interpreter_item[
                'version'],  interpreter_item['conda-name']
            args = (os_name, arch,version, conda_name)
            build_process(*args)

    pass


if __name__ == "__main__":
    config_file = os.path.join("deployment", "interpreters.json")
    with open(config_file, "r", encoding="utf-8") as f:
        d = json.load(f)
    build(d)
