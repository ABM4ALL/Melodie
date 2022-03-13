import json
import re
from flask import Blueprint, request
from Melodie.templates.create_template import create_project, new_project_config_default
from .messages import Response

tools = Blueprint('tools', __name__)


def name_convert_to_snake(name: str) -> str:
    """驼峰转下划线"""
    if '_' not in name:
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    else:
        raise ValueError(f'{name}字符中包含下划线，无法转换')
    return name.lower()


@tools.route('test', methods=['get'])
def test():
    return Response.ok("Ok")


@tools.route('createProject', methods=['post'])
def create_new_project():
    data = json.loads(request.data)
    for k, v in data.items():
        k = name_convert_to_snake(k)
        print(k, v)
    new_project_config = new_project_config_default.copy()
    new_project_config['path'] = data['directory']
    new_project_config['name'] = data['projectName']
    new_project_config['alias'] = data['projectNameAlias']
    try:
        create_project(new_project_config)
        return Response.ok("Project created!")
    except FileExistsError as e:
        return Response.error(str(e))
