import os
import time
from base import is_pypy, OUTPUT_DIR
from MelodieInfra.table import PyAMTable, TableReader, TableWriter
from sqlalchemy import Integer

PATH = os.path.join(os.path.dirname(__file__), "data", "pyam_tutorial_data.csv")

EXCEL_FILE_TO_WRITE = os.path.join(OUTPUT_DIR, "test-out.xlsx")


def test_csv_reader():
    header, rows = TableReader(PATH)._read_csv()
    assert len(list(rows)) == 1026


def test_excel_writer():
    writer = TableWriter(EXCEL_FILE_TO_WRITE).write()
    writer.send(["a", "b", "c"])
    for i in range(10):
        writer.send([i, i * 2, i * 3])
    writer.close()
