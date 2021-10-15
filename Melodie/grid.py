


# Grid跟network不同，它是一张脱离agents存在的地图，上面是一个个地块，每个地块有自己的属性，其实每个地块也类似于一个agent，只不过行为上简单、被动一点儿，不乱跑。
# 在城市土地规划的例子里，每个地块可能有不同的用途规定，在模拟过程中可改变。
# 在狼、羊、草的例子里，地块上长草、被吃、再长。
# 在森林大火的例子里，地块上的植物可能被其他地块上的火引燃——所以也有互动。


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