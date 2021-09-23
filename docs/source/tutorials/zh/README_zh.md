# 项目结构

目前仅支持使用sqlite数据库进行数据的存储。

在目前，sqlite文件的名称与项目名称相同。
启动时，需要通过Config对象来设置这些参数,如下述代码所示：
```python
run(
        GINIAgent,
        GiniEnvironment,
        Config('WealthDistribution', os.path.dirname(__file__)),
    )
```
Config的参数含义：
1. 第一个参数，是项目的名称，只允许有效的变量名。
除了字母、数字、下划线之外，还可以使用汉字、日韩文字、阿拉伯文字等非Ascii字符。
2. 第二个参数是项目的根目录。默认情况下，数据库文件以及分析结果文件将输出到项目`根目录/_database`和`根目录/_output`下。
3. 还有其他参数，可以指定数据库和结果文件的输出路径。

## 数据库与存储
数据存储方面，
一共有4个数据表：
- scenarios，存储生成的scenario
  - 仿真最开始的阶段，被ScenarioManager生成后即写入数据库。
- agent_param，存储agent的参数
  - 当刚刚进入一个Scenario时，被TableGenerator生成后即写入数据库
- env_result，存储环境的结果信息
  - 每一个Scenario结束时，被写入数据库。
- agent_result，存储agent的结果
  - 写入数据库的时间与env_result相同。

可以使用dbbrowser打开数据库，或者用Melodie.db.create_conn()生成一个
数据库管理的实例，调用其中的相应方法来查看数据。

例如要获取环境的数据：
```python
from Melodie.db import create_db_conn
create_db_conn().query_env_results()
```
返回结果：
```text
     trade_num  win_prob  total_wealth      gini  scenario_id  step
0          100       0.6        5398.0  0.304265            0     0
1          100       0.6        5445.0  0.303590            0     1
2          100       0.6        5487.0  0.303246            0     2
3          100       0.6        5530.0  0.300807            0     3
4          100       0.6        5583.0  0.299995            0     4
..         ...       ...           ...       ...          ...   ...
195        100       0.6       15026.0  0.289315            0   195
196        100       0.6       15076.0  0.289395            0   196
197        100       0.6       15128.0  0.289357            0   197
198        100       0.6       15182.0  0.289106            0   198
199        100       0.6       15222.0  0.289137            0   199

[200 rows x 6 columns]

```
其他可详见`tests/test_db.py`

**另外，与Melodie配套的、基于Web的管理工具，将带有数据库的初步查看功能。**

由于可能涉及到仿真过程中对数据库的异步读写，所以目前阶段，create_conn()每次都返回一个
新的数据库连接。这可能会导致较大的读写开销。在未来将考虑进行优化。

## Scenario的生成——ScenarioManager
Melodie仿真的项目，首先可以分为一系列的场景（Scenario）。

一系列场景由ScenarioManager的`gen_scenario()`方法生成。仿真过程中，
**对于每一个场景，都会单独创建一个模型并运行仿真**。

- 场景的概念略微有一些复杂。因此对于入门级的项目应该省掉这个概念，用最简单的方式来入门。

- 另外，不同场景之间的数据是独立的，因此用户必然会提出并行仿真不同Scenario的要求。
为了解决这个问题，需要在向sqlite写入数据时进行一定的判断，如果写入失败，则进行等待。


## Agent的参数生成——TableGenerator的使用

场景生成后，第一步任务就是要生成Agent的参数，也就是用TableGenerator.

TableGenerator的使用方法较为简单，只要重写其`setup()`函数即可。
在以下代码中，假设Agent需要赋初始值的属性——也就是参数(parameter)——有`productivity`和
`account`两个，那么就调用`add_agent_param`方法即可。
```python
import numpy as np
from Melodie.table_generator import TableGenerator


class GiniTableGenerator(TableGenerator):

    def setup(self):
        self.add_agent_param('productivity', self.scenario.agent_productivity)
        self.add_agent_param('account', lambda: float(np.random.randint(self.scenario.agent_account_min,
                                                                        self.scenario.agent_account_max)))

```
add_agent_param方法有两个参数。第一个是属性名称，第二个是生成器。

生成器是int/float/str型，或者是一个函数，没有参数，返回一个相应数据类型的数值。

当传入int/float/str型数时，所有Agent被设置的属性，都和传入的值一样。如第一行初始化
productivity，所有的Agent的productivity都被设置为`scenario.agent_productivity`

当传入函数时，属性将被设置为这个函数调用后的返回值。

TableGenerator在生成参数之后，就会将参数存入数据库内。存入数据库之后，
它的任务就完成了。

