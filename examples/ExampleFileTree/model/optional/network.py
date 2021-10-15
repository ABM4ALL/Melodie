
# network是定义在agent上的，不像grid那么独立。没有人，地球上依然有土地。但是，没有人，也有不存在“人和人之间的关系”了。
# 用一张矩阵记录agent之间的【关系】，关系又可以有多个属性，方向、每个方向的强弱等。
# agent和env都可以访问network并修改agent之间的【关系】
# run_model的可选项，如果选了，就初始化到model里

class Relation:
    pass

class Network:
    pass