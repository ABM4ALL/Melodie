
# --------
# optional
# --------

# 每个spot是一个格子，很多个spot构成一个grid。
# 每个spot可以有多个属性。
# grid记录每个agent的站立的位置。

# agent和env都可以访问grid并修改：
# 1. agent的位置。
# 2. spot的属性。

# grid是run_model的可选项，如果选了，就初始化到model里

class Spot:
    pass

class Grid:
    pass