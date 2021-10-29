# -*- coding:utf-8 -*-
# @Time: 2021/9/23 16:32
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: server.py
# copy static files: scp -r hzy@192.168.50.211:/home/hzy/Documents/Developing/web/melodie-fe/build/* ./Melodie/static
import json
import math
import os
import random
import tempfile
import sqlite3
from flask import Flask, request, make_response
import pandas as pd

from flask_cors import CORS
from werkzeug.utils import redirect

from Melodie.management.experiment_status import ExperimentStatus
from Melodie.management.project_structure import list_all_files, get_all_function_cfgs, to_mermaid, get_all_funcdefs, \
    get_flow, to_digraph

app = Flask(__name__, static_folder='../static', static_url_path='', )

CORS(app, resources=r'/*')  # 注册CORS, "/*" 允许访问所有api


@app.after_request
def after(resp):
    '''
    被after_request钩子函数装饰过的视图函数
    ，会在请求得到响应后返回给用户前调用，也就是说，这个时候，
    请求已经被app.route装饰的函数响应过了，已经形成了response，这个时
    候我们可以对response进行一些列操作，我们在这个钩子函数中添加headers，所有的url跨域请求都会允许！！！
    '''
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    # resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type,x-custom-header'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    return resp


def read_sql(db_path, sql):
    conn = sqlite3.connect(db_path)

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        res = pd.read_sql(sql, conn)
        conn.close()
        res.to_json(tf.name, orient='table', indent=4, index=False)
        data = tf.read()
        tf.close()
    return data


@app.route('/meta')
def get_meta():
    cwd = os.getcwd()
    sqlite_file_list = []
    for root, dirs, files, in os.walk(cwd):
        for file in files:
            if file.endswith('sqlite'):
                path = os.path.join(root, file)
                path = path.replace('\\', '/')
                sqlite_file_list.append(path)
    return json.dumps(sqlite_file_list)


@app.route('/sqlite_desc')
def browse_sqlite():
    db_path = request.args.get('db_path')
    print(db_path)
    assert os.path.exists(db_path)
    ret = read_sql(db_path, "select tbl_name from sqlite_master")
    return ret


@app.route('/all_func_defs')
def get_all_defs():
    files = list_all_files(os.getcwd(), {'.py'})
    res = []
    for file in files:
        res.append({'title': os.path.basename(file),
                    'key': file,
                    'children': [
                        {'title': f.name,
                         'key': file + f.name,
                         'file': file,
                         'func_name': f.name
                         } for f in get_all_funcdefs(file)
                    ]})
    return json.dumps(res)


def get_mermaid(file, func_name):
    flow, edge_tags = get_flow(file, func_name)
    dig = to_digraph(flow, edge_tags)
    mermaid = to_mermaid(dig)
    return mermaid


@app.route('/get_mermaid')
def handle_mermaid():
    file = request.args.get('file')
    func_name = request.args.get('func_name')

    return json.dumps({
        'mermaid': get_mermaid(file, func_name)
    })


@app.route('/data')
def handle_data():
    db_path = request.args.get('db_path')
    current_table_name = request.args.get('table_name')
    return read_sql(db_path, f'select * from {current_table_name}')


@app.route('/space')
def handle_space_data():
    import json
    return json.dumps([{'id': i, 'x': random.randint(10, 590), 'y': random.randint(10, 590)} for i in range(100)])
    # return


@app.route('/code', methods=['POST'])
def handle_code():
    code_files = json.loads(request.data)
    for file in code_files:
        with open(os.path.join(os.path.dirname(__file__), 'files', file), 'w') as f:
            f.write(code_files[file])
    return ''


@app.route('/get_code', methods=['GET'])
def handle_get_code():
    with open(os.path.join(os.path.dirname(__file__), 'files', 'test.xml'), 'r') as f:
        return f.read()


@app.route('/simulation-status', methods=['GET'])
def handle_get_simulation_status():
    return ExperimentStatus(
        finished_run_ids=[(0, 1), (0, 2)],
        current_run_ids=[(0, 3), (1, 1)],
        waiting_run_ids=[(1, 2), (1, 3)]
    ).to_json()


with open(os.path.join(os.path.dirname(__file__), "files", "graph-demo-with-layout.json")) as f:
    graph = json.load(f)


@app.route("/network-demo", methods=['GET'])
def handle_graph():
    nodes = len(graph["series"]["data"])
    for i in range(nodes):
        if random.random() > 0.5:
            graph['series']['data'][i]['category'] = 1
        else:
            graph['series']['data'][i]['category'] = 0
    return json.dumps(graph)


@app.route('/')
def handle_root():
    return redirect('http://localhost:8090/index.html', code=301)


def run_server():
    app.run(host='0.0.0.0', port=8089)


def run():
    app.run(host='0.0.0.0', port=8089)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)
