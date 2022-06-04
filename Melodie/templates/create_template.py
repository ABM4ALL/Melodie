# -*- coding:utf-8 -*-
import os.path
import shutil

import chardet

properties = {
    "_NAME_": "Demostration",
    "_ALIAS_": "Demo",
    "_CREATED_AT_": "",
    "_AUTHOR_": "",
    "_EMAIL_": "",
}

new_project_config_default = {
    "alias": "Demo",
    "name": "Demonstration",
    "path": "",  # create project folder at this folder. for example: if 'path'=c:\users\username\desktop, then
    # all project files will be placed at c:\users\username\desktop\Demonstration
}
_d = os.path.dirname
TEMPLATE_ROOT = os.path.join(_d(__file__), "NewTemplate", "_NAME_")


def create_project(project_config):
    assert os.path.exists(
        project_config["path"]
    ), f'The directory {project_config["path"]} was not found!'
    project_root = os.path.join(project_config["path"], project_config["name"])
    shutil.copytree(TEMPLATE_ROOT, project_root)
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith((b".py", b".md", b".txt")):
                file_abs_path = os.path.join(root, file)
                with open(file_abs_path, "rb") as f:
                    bs = f.read()
                print(file, chardet.detect(bs))
                encoding = chardet.detect(bs)["encoding"]
                if encoding is not None:
                    b_formatted = (
                        bs.decode(encoding)
                        .replace("_ALIAS_", project_config["alias"])
                        .encode(encoding)
                    )
                    b_formatted = (
                        b_formatted.decode(encoding)
                        .replace("_NAME_", project_config["name"])
                        .encode(encoding)
                    )
                    with open(file_abs_path, "wb") as f:
                        f.write(b_formatted)


if __name__ == "__main__":
    EXAMPLE_ROOT = os.path.join(_d(_d(_d(__file__))), "examples")
    new_project_config = new_project_config_default.copy()
    new_project_config["path"] = EXAMPLE_ROOT
    create_project(new_project_config)
