
import numpy as np

if __name__ == "__main__":
    m = np.zeros((3,6))
    k1 = np.array([1,2,3,4,5,6])
    k2 = np.array([2, 3, 4, 5, 6, 7])
    k3 = np.array([3, 4, 5, 6, 7, 8])
    l = [k1, k2, k3]
    for ll, values in enumerate(l):
        print(ll)
        print(values)
        m[ll,:] = values
    print(m)
