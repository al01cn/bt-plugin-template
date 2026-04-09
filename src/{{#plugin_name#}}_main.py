#!/usr/bin/python
# coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------

import sys
import os
import json

# 设置运行目录
os.chdir("/www/server/panel")

data_path = os.path.join("/www/server", "{{#plugin_name#}}") # 插件数据根目录

# 添加包引用位置并引用公共包
sys.path.append("class/")
import public # type: ignore

# 在非命令行模式下引用面板缓存和session对象
if __name__ != '__main__':
    from BTPanel import cache, session, redirect # type: ignore

# 插件主程序类
class plugin_name_main:
    """宝塔插件 DEMO - 后端主程序

    类名必须与文件名（不含 _main 后缀）一致。
    前端通过 plugin?action=a&s=方法名&name=demo 调用。
    """

    __plugin_path = "/www/server/panel/plugin/{{#plugin_name#}}/"
    __config = None

    def __init__(self):
        pass

    # 访问 /demo/index.html 时调用，需要在 templates 中有 index.html
    def index(self, args):
        return self.ping(args)

    def ping(self, args):
        """心跳测试，验证前后端通信"""
        import time
        return {
            "status": True,
            "msg": "Hello World! 插件运行正常。",
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    # 读取配置项(插件自身的配置文件)
    # @param key   取指定配置项，若不传则取所有配置 [可选]
    # @param force 强制从文件重新读取配置项 [可选]
    def __get_config(self, key=None, force=False):
        if not self.__config or force:
            config_file = self.__plugin_path + 'config.json'
            if not os.path.exists(config_file):
                return None
            f_body = public.ReadFile(config_file)
            if not f_body:
                return None
            self.__config = json.loads(f_body)

        if key:
            if key in self.__config:
                return self.__config[key]
            return None
        return self.__config

    # 设置配置项(插件自身的配置文件)
    # @param key   要被修改或添加的配置项 [可选]
    # @param value 配置值 [可选]
    def __set_config(self, key=None, value=None):
        if not self.__config:
            self.__config = {}

        if key:
            self.__config[key] = value

        config_file = self.__plugin_path + 'config.json'
        public.WriteFile(config_file, json.dumps(self.__config))
        return True
