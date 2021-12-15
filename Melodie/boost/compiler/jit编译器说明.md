# 功能流程
1、扫描Agent和Environment中的setup方法，获取属性信息并且生成数据类型
- AgentList的类型，需要新的解决方案。
- 
2、将用户注册的、不可识别的数据类型，编译成jitclass。
- 允许的数据类型：int,float,str;
- agent, agent_list 和 environment

3、将Agent和Environment编译成一系列独立函数。


## 生成的文件包含以下部分：
1. 导入部分，导入所有有关的包
2. 所有agent_list和agent的数据。只要一个空的矩阵就可以了。
3. 用户注册的自定义class类型
4. Agent和Environment的独立函数
5. Model的run函数。

## 编译流程
1. 扫描所有被编译的类所在的文件中，用到的包，以及相关的导入信息。
   - 导入语句直接运行即可
2. 扫描Agent\Environment的初始化语句中调用到的各种类型，Agents/Environments应该有相应的
数据类型。生成一个数组即可。

3. 扫描所有自定义的类，并且编译为jitclass

4. 扫描Agent\Environment和Model，生成代码.


### 3和4两部分需要做到的内容有：

1、进行类型推导，扫描出相应的类型。
2、对于为agent/agent_list/environment型的变量，需要将其方法改写成变量名，
并且相关的函数调用也要写成独立的函数。需要将其方法拆散，并且去除相关的内容。
3、对于agent/agent_list和environment型的变量，需要将其属性访问从`a.xxx`改写成`a['xxx']`