import random


class ID(int):
    def __init__(self, value: int):
        super().__init__(value)

        pass


def a():
    b = random.randint(10000, 100000)
    print(id(b))
    return b


def a1():
    b = random.randint(10000, 100000)
    print('id_b', id(b))
    return (b,)


c = a()
print(id(c))

c1 = a1()
print('id_b1', id(c1[0]))
for i in c1:
    print('id_b1', id(i))
