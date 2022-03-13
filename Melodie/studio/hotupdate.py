from __future__ import print_function

import time
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

observer: Optional[Observer] = None


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, watch_path: str, callback: Callable[[], None]):
        super(FileMonitorHandler, self).__init__()
        self._watch_path = watch_path
        self._callback = callback

    def on_any_event(self, event: FileSystemEvent):
        print(event.src_path)
        if event.src_path.endswith(".py"):
            self._callback()


def start_watch_fs(watch_dir: str, callback: Callable[[], None]):
    global observer
    assert observer is None
    event_handler = FileMonitorHandler(watch_dir, callback)
    observer = Observer()
    observer.schedule(event_handler, path=watch_dir, recursive=True)  # recursive递归的
    observer.start()


if __name__ == "__main__":
    start_watch_fs(".", lambda: print("file changed!"))
    while 1:
        time.sleep(1)
