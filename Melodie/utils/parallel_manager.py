import base64
import json
import os.path
import queue
import sys
import threading
import time
from typing import List, Tuple

import cloudpickle
from rpyc import Service
from rpyc.utils.server import ThreadedServer
import subprocess


class Tasks:
    def __init__(self):
        self.config = {}
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def put_task(self, item):
        self.task_queue.put(item)

    def get_task(self):
        try:
            return self.task_queue.get(block=False)
        except queue.Empty:
            return None

    def put_result(self, item):
        self.result_queue.put(item)

    def get_result(self):
        return self.result_queue.get()

    def get_config(self):
        return self.config


tasks: Tasks = None


class ParallelManager:
    def __init__(self, cores: int, configs: Tuple):
        self.th_server = threading.Thread(target=self.run_server)
        self.processes: List[subprocess.Popen] = []
        self.cores = cores
        self.server: ThreadedServer = None
        self.set_tasks(configs)

    def set_tasks(self, config):
        global tasks
        tasks = Tasks()
        tasks.config = config

    def put_task(self, task):
        tasks.put_task(task)

    def get_result(self):
        return tasks.get_result()

    def run_server(self):
        self.server = ThreadedServer(service=TimeService, port=12233, auto_register=False)
        self.server.start()

    def run(self, role: str):
        assert role in {'calibrator', 'trainer'}
        self.th_server.setDaemon(True)
        self.th_server.start()
        for core_id in range(self.cores):
            p = subprocess.Popen(
                [sys.executable,
                 os.path.join(os.path.dirname(__file__), "parallel_worker.py"),
                 "--core_id", str(core_id),
                 "--workdirs", json.dumps([os.getcwd()]),
                 "--role", role
                 ])
            self.processes.append(p)

    def close(self):
        for p in self.processes:
            p.terminate()
        self.server.close()
        global tasks
        tasks = None


class TimeService(Service):

    # 对于服务端来说， 只有以"exposed_"打头的方法才能被客户端调用，所以要提供给客户端的方法都得加"exposed_"
    def exposed_get_time(self):
        return time.ctime()  # time模块中的一个内置方法

    def exposed_get_task(self):
        return json.dumps(tasks.get_task())

    def exposed_put_result(self, result):
        loaded = cloudpickle.loads(base64.b64decode(result))
        tasks.put_result(loaded)

    def exposed_get_config(self):
        return json.dumps(tasks.get_config())


if __name__ == "__main__":
    ParallelManager().run()
    time.sleep(5)
