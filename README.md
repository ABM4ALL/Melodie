# README

### Next steps

Songmin
* 修改例子写tutorial
  * 例1 - VirusContagion在tutorial里一步步讲：先把没有grid和network的部分讲完，跑通并呈现结果，然后再加另外两个模块。最后再加可视化什么的。
  * 例2 - Brock and Hommes的模型，calibrator + trainer都可以用，两个版本。也在Tutorial里详细分步讲，先simulator。 
  * clean analyzer and plotter --> 这两个还是不作为Melodie的部分一起发布了吧，可以放在examples/gallery里提到。
* revision
  * get_registered_dataframe --> get_df (changes like this: keep both and add expiring reminder)
  * load_dataframe --> load_df (define MelodieDataframe)
  * excel_source --> input, 去掉sqlite文件夹，放到output里，如果用户需要其他的，让他们自己弄。
  * register_generated_dataframes --> generate_agent_dataframe (统一table和df的叫法)，此外，table_generator也可以叫agent_dataframe_generator
  * log信息时间取两位小数
  * define_basic_components这个名字也比较模糊，不如分拆成env和data_collector各一个了？
  * create_agent_container这里container也是多了一个概念
  * agent and env results --> order of columns, 把结果表里的step（从1开始？）改成period
  * ModelRunRoutine --> use "iterator" in the name, e.g. ModelIterator
  * save df to output folder as excel files


Zhanyi
* python版本适配
* 一个项目模板 -- 文件夹结构、CI、test等workflow 
* 生成文档的api reference
  * 写批注
  * 给内置函数加下划线
* 合并modules（参考docs里的overview


Other
* Plan ABM4ALL organization page
  * library --> papers
  * articles in Chinese? (from WeChat)
  * discussion platform? (Q&A)
* working with Git
  * separate branch
  * create issues --> squash and merge, changelog



[![Build status](https://app.travis-ci.com/SongminYu/Melodie.svg?token=qNTghqDqnwadzvj4y4z7&branch=master&status=passed)](https://travis-ci.com/SongminYu)

This project is supposed to be developed as a general framework that can be used to establish agent-based models for
specific uses. Current main contributors are **Songmin YU** and **Zhanyi HOU**.

### Supported Python Versions

Python from 3.7~3.9

PyPy interpreter is also supported. But Melodie is not designed for PyPy interpreter, so the performance may not be
improved significantly.

### Run this project

```shell
git clone xxxx
pip install Cython pytest
python.exe setup.py build_ext --inplace
pytest
```

### Build docs

```shell
cd docs
sphinx-autobuild source build/html
# click the link appeared in the console to view the documentation website.
```

As for auto-generated API Documentation, run this command to update:
```shell
python setup.py build_ext -i
sphinx-build source build/html -E -a
```

### Run examples

examples are at the `examples/` folder.


### Melodie studio

Melodie has an integrated web-based GUI tool for creating new projects and database viewing. you could start it with
this command:

```sh
python -m Melodie studio
```

or if you have created a project, you could use the studio in a Python script:

```python3
import os

from Melodie.studio.main import studio_main
from Melodie import Config

config = Config(
    project_name='DemoProject',
    project_root=os.path.dirname(__file__),
    sqlite_folder='data/sqlite',
    excel_source_folder='data/excel_source',
    output_folder='data/output',
)

studio_main(config)
```

then visit `http://localhost:8089/` with browser

