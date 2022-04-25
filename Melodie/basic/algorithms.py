def binary_search(lis, num, key):
    left = 0
    right = len(lis) - 1
    mid = 0
    if key is None:
        key = lambda x: x
    while left <= right:
        mid = (left + right) // 2
        if num < key(lis[mid]):
            right = mid - 1
        elif num > key(lis[mid]):
            left = mid + 1
        else:
            return mid

    if mid == 0:
        return 0
    else:
        return -1
