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
from flask import Flask, request
import pandas as pd

from flask_cors import CORS
from werkzeug.utils import redirect

app = Flask(__name__, static_folder='../static', static_url_path='', )

CORS(app, resources=r'/*')  # 注册CORS, "/*" 允许访问所有api


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


@app.route('/')
def handle_root():
    # 永久重定向到新网址到百度
    return redirect('http://localhost:8089/index.html', code=301)


def run():
    app.run(host='0.0.0.0', port=8089)


if __name__ == '__main__':
    # run()
    app.run(host='0.0.0.0', port=8089)
