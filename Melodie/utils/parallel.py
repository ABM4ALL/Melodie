import base64
import importlib
import json
import multiprocessing
import queue
import sys
import time
from typing import Dict, Tuple, Any

import cloudpickle

from Melodie.global_configs import MelodieGlobalConfig
from Melodie.utils.system_info import is_windows

params_queue = multiprocessing.Queue() if not is_windows() else queue.Queue()
result_queue = multiprocessing.Queue() if not is_windows() else queue.Queue()
