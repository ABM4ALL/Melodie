import base64
import json
import logging
import os.path
import queue
import subprocess
import sys
import threading
import time
from typing import List, Optional, Tuple

import cloudpickle
from rpyc import Service
from rpyc.utils.server import ThreadedServer

logger = logging.getLogger("ParallelManager-MainThread")

tasks: Optional["Tasks"] = None


class Tasks:
    def __init__(self):
        self.config = {}
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def put_task(self, item):
        self.task_queue.put(item)

    def get_task(self):
        while 1:
            try:
                task = self.task_queue.get(block=False)
                logger.debug(f"got task {task}")
                if task is not None:
                    return task
            except queue.Empty:
                continue

    def put_result(self, item):
        self.result_queue.put(item)

    def get_result(self):
        while 1:
            try:
                return self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue

    # def get_result_nowait(self):
    #     return self.result_queue.get()

    def get_config(self):
        return self.config


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
        try:
            self.server = ThreadedServer(
                service=ParallelDataService, port=12233, auto_register=False
            )
            self.server.start()
        except OSError as e:
            import traceback

            traceback.print_exc()
            raise Exception("Server Error Occurred, exiting...")

    def run(self, role: str):
        """
        Run subprocesses

        :param role: run as calibrator or trainer
        :return:
        """
        assert role in {"calibrator", "trainer", "simulator"}
        self.th_server.setDaemon(True)
        self.th_server.start()
        for core_id in range(self.cores):
            p = subprocess.Popen(
                [
                    sys.executable,
                    os.path.join(os.path.dirname(__file__), "parallel_worker.py"),
                    "--core_id",
                    str(core_id),
                    "--workdirs",
                    json.dumps([os.getcwd()]),
                    "--role",
                    role,
                ],
                # env={"PYTHONPATH": ";".join(sys.path)},
            )
            self.processes.append(p)

    def close(self):
        """
        Close all subprocesses

        :return:
        """
        for p in self.processes:
            p.terminate()
            logger.info(f"terminated subworker {p}")
        if self.server is not None:
            self.server.close()
            logger.info("Server closed!")
        global tasks
        tasks = None


class ParallelDataService(Service):
    def exposed_get_time(self):
        return time.ctime()

    def exposed_get_task(self):
        return base64.b64encode(cloudpickle.dumps(tasks.get_task()))

    def exposed_put_result(self, result):
        loaded = cloudpickle.loads(base64.b64decode(result))
        tasks.put_result(loaded)

    def exposed_get_config(self):
        return json.dumps(tasks.get_config())
