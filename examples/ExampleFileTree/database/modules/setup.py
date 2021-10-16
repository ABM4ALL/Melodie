

class TableRegister:
    # 注册每一张static表的调用变量名、表名、列名、列数据类型。虽然麻烦，但可以帮助用户少犯错。
    # 可能要单独写一个class MelodieTable？
    pass

# 根据TableRegister，把data/excel_source里的表导入到sqlite，并创建sqlite文件。之后，运行模型的时候就所有都是sqlite了。
# 如果有static tables，启动run_model的一开始，默认就把它们一起都load到内存里（如果有特别大的表可以单独去掉）。

# 用户主要是准备一张Scenarios的excel表，其他的：
# 1. 不必知道scenario_manager这回事
# 2. 写scenario.py的文件（照抄一遍column_name） --> 甚至连这个都不用了？
# 3. 在agent或env里通过scenario访问情景参数、static tables里的数据

# 问题：linux里如果没有excel会存在问题吗？
