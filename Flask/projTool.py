"""
这个文件用于自定义一些项目中会用到的工具函數和类
"""
import json

def configReader(configKey=None,file="Flask/config.json") -> str:
    "这个方法用来获取config.json文件中的配置"
    with open(file) as file:
        if configKey is None:
            return json.load(file)
        else:
            return json.load(file)[configKey]