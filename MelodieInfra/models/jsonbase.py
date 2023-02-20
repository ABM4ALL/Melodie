# -*- coding:utf-8 -*-
# @Time: 2023/2/18 17:48
# @Author: Zhanyi Hou
# @Email: 1295752786@qq.com
# @File: jsonbase.py

class JSONBase:
    names_map = {}

    def to_json(self):
        d = {}
        for k, v in self.__dict__.items():
            k = k if k not in self.__class__.names_map else self.__class__.names_map[k]
            if k.startswith("_"):
                continue
            elif hasattr(v, "to_json"):
                d[k] = v.to_json()
            elif isinstance(v, dict):
                new_dict = {}
                for new_k, new_v in v.items():
                    if hasattr(new_v, "to_json"):
                        new_dict[new_k] = new_v.to_json()
                    else:
                        new_dict[new_k] = new_v
                d[k] = new_dict
            elif isinstance(v, (list, tuple)):
                new_list = []
                for new_v in v:
                    if hasattr(new_v, "to_json"):
                        new_list.append(new_v.to_json())
                    else:
                        new_list.append(new_v)
                d[k] = new_list
            else:
                d[k] = v
        return d