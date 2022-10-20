import time

import pandas as pd


class MyData:
    def __init__(self, df: pd.DataFrame):
        self.records = df.to_dict("records")
        self.indices = {
            "id": {record["id"]: {row} for row, record in enumerate(self.records)}
        }

    def get_data(self, **kwargs):
        s: set = None
        for arg_name, arg_value in kwargs.items():
            indices = self.indices[arg_name][arg_value]
            if s is None:
                s = indices
            else:
                s = s.intersection(indices)
        records = []
        for row in s:
            records.append(self.records[row])
        if len(records) == 1:
            return records[0]
        return records


df = pd.DataFrame([{"a": 1, "b": 1, "id": i} for i in range(10000)])
df.set_index(["id"])

M = 100000


def df_getitem_speed():
    s = 0
    t0 = time.time()
    for i in range(M):
        a = df.loc[9999, "b"]
        # s += a
    print("df:", time.time() - t0)


def mycls_getitem_speed():
    s = 0
    my_data = MyData(df)
    t0 = time.time()
    for i in range(M):
        a = my_data.get_data(id=9999)
        s += a["b"]
    print("mycls", time.time() - t0)


df_getitem_speed()
mycls_getitem_speed()
