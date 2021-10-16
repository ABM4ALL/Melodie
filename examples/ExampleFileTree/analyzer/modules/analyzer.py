


# 每次run模型未必需要run analyzer，而且对于一次run的结果，也可能run多次analyzer。基本上，跑analyzer和跑model是独立的两件事。
# 因此，在文件夹的地位上，analyzer应该是跟model平齐的。相应的，把_output文件夹放在analyzer里。
# 针对这个analyzer，Melodie其实基本就只提供一个空的类，只需要有一些数据库相关的支持，方便读取、写入。



