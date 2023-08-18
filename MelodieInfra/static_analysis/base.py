from abc import ABC, abstractmethod
import ast
from dataclasses import dataclass
import os
from typing import List, Literal, Tuple


class CheckerMessage:
    def __init__(self, status:  Literal['error', 'warning'], lineno: int) -> None:
        self.status = status
        self.filename: str = ''
        self.lineno = lineno

    @property
    def message(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"[{self.status} {self.__class__.__name__}] at {self.filename}:{self.lineno}: {self.message}"


class BaseChecker(ABC):
    @abstractmethod
    def check(self, ast_node: ast.AST) -> CheckerMessage:
        pass


class StaticCheckerRoutine:
    checkers: List[BaseChecker] = []

    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.messages: List[CheckerMessage] = []

    def check(self, file_path: str):
        """
        Convert file to AST, then dispatch it to all checkers.
        """
        with open(file_path, 'r', encoding="utf-8", errors="replace") as f:
            ast_root = ast.parse(f.read())
            for checker_cls in self.__class__.checkers:
                msg: CheckerMessage
                for msg in checker_cls().check(ast_root):
                    if msg is not None:
                        msg.filename = file_path
                        self.messages.append(msg)

    def run(self):
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(".py"):
                    try:
                        print("parsing file:", file_path)
                        self.check(file_path)
                    except KeyboardInterrupt as e:
                        raise e
                    except:
                        pass
        for msg in self.messages:
            print(msg)


if __name__ == "__main__":
    r = StaticCheckerRoutine(".")
    r.run()
