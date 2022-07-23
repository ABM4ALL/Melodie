# README

### Next steps

Songmin
* 修改例子：
  * 例1 - VirusContagion用simulator + grid + network。在tutorial里一步步讲：先把没有grid和network的部分讲完，跑通并呈现结果，然后再加另外两个模块。最后再加可视化什么的。
  * 例2 - Brock and Hommes的模型，calibrator + trainer都可以用，两个版本。也在Tutorial里详细分步讲，先simulator。 
  * clean analyzer and plotter
* 写tutorial
* Plan ABM4ALL organization page
  * library --> papers
  * articles in Chinese? (from WeChat)
  * discussion platform? (Q&A)
* working with Git
  * separate branch
  * create issues --> squash and merge, changelog
* revise some names
  * get_registered_dataframe --> get_df (keep both and add expiring reminder)
  * excel_source --> input (csv?)


Zhanyi
* python版本适配
* 一个项目模板 -- 文件夹结构、CI、test等workflow 
* 生成文档的api reference
  * 写批注
  * 给内置函数加下划线
* 合并modules（参考docs里的overview



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

