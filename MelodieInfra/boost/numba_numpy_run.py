from numba import njit
import numpy as np
import pandas as pd

df = pd.DataFrame([[1, 1.0], [2, 2.2]], columns=["id", "name"])
arr = df.to_numpy()
print(arr, arr.dtype, df["id"].dtype, df["id"].to_numpy().dtype)

arr = np.array([(1, 1.0), (2, 2.2)], dtype=[("id", "i4"), ("value", "f4")])
# fields_gl = ('a1', 'a2')
print(arr)


@njit
def test(arr):
    s = 0.0
    for item in arr:
        s += item[0]
    return s


print(test(arr))
