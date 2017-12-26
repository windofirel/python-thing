import json
import shutil
import os
import apk
import datetime
from tkinter import *
import tkinter.messagebox as msgbox

__author__ = 'dongbaicheng'
__date__ = '2017/12/25'


# 移动apk文件、修改config文件
class AutoRelease:
    def __init__(self):
        if os.path.exists('./config_data.txt'):
            with open('./config_data.txt', 'r') as data:
                self.source_path = data.readline().strip().split('#')[1]
                self.root_target_path = data.readline().strip().split('#')[1]
                self.pkg_prefix = data.readline().strip().split('#')[1]
        else:
            self.root_target_path = 'D:/apk'
            self.source_path = 'D:/Program Files/Jenkins/workspace/CI DEMO/apk'
            self.pkg_prefix = 'com.chinasie.'

        self.target_path = os.path.join(self.root_target_path, 'plugin')
        self.cfg_file_path = os.path.join(self.root_target_path, 'config.json')
        self.current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 初始化目标目录
    def init_directories(self):
        platform_dir = os.path.join(self.root_target_path, 'platform')
        if not os.path.exists(platform_dir):
            os.makedirs(platform_dir)

        plugin_dir = os.path.join(self.root_target_path, 'plugin')
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)

        if not os.path.exists(self.cfg_file_path):
            self.create_config_file()

    # 移动apk到发布目录
    def move_apk(self):
        for file_name in os.listdir(self.source_path):
            if file_name.endswith('.apk'):
                src = os.path.join(self.source_path, file_name)
                target = os.path.join(self.target_path, file_name.replace("-debug", ""))
                shutil.copy(src, target)
                print("copy file " + file_name + " success")

    # 修改配置文件
    def update_config(self):
        # 检测配置文件 不存在就生成
        if not os.path.exists(self.cfg_file_path):
            self.create_config_file()
            return
        # 只修改更新的插件的版本号 添加新增插件的配置
        with open(self.cfg_file_path, 'r') as config_file:
            config_json = config_file.read()
        files = os.listdir(self.target_path)
        configs = json.loads(config_json, object_hook=apk.Apk.json_2_obj)
        # 删掉不存在的apk的配置信息
        for config in configs:
            if not files.count(config.name) and config.name != 'PluginMain.apk':
                configs.remove(config)
        # 根据apk信息更新配置信息
        for file in files:
            if not file.endswith('.apk'):
                continue
            file_path = os.path.join(self.target_path, file)
            modify_stamp = os.path.getmtime(file_path)
            file_time = datetime.datetime.fromtimestamp(modify_stamp)
            contain_file = False  # 用于判断文件是否存在相应配置信息
            for config in configs:
                if config.name == file:
                    contain_file = True
                    config_time = datetime.datetime.strptime(config.updateTime, '%Y-%m-%d %H:%M:%S')
                    # apk文件修改时间大于配置文件的更新时间时，配置信息版本号+0.01，更新时间修改为当前时间
                    if config_time < file_time:
                        config.updateTime = self.current_time
                        config.version = str(float(config.version) + 0.01)
                    break
            # 添加新apk的配置信息
            if not contain_file:
                configs.append(self.create_plugin_module(file))

        # 写入配置文件
        config_json = json.dumps(configs, default=lambda o: o.__dict__, sort_keys=True, indent=4)

        with open(self.cfg_file_path, 'w') as config_file:
            config_file.write(config_json)
            config_file.flush()

    # 创建配置文件
    def create_config_file(self):
        list = []
        platform_obj = self.create_platform_config('PluginMain.apk')
        list.append(platform_obj)

        for file_name in os.listdir(self.target_path):
            plugin_obj = self.create_plugin_module(file_name)
            list.append(plugin_obj)
        config_json = json.dumps(list, default=lambda o: o.__dict__, sort_keys=True, indent=4)

        with open(self.cfg_file_path, 'w') as config_file:
            config_file.write(config_json)
            config_file.flush()

    # 创建插件模块的对象并返回
    def create_plugin_module(self, file_name):
        pkg_name = self.pkg_prefix + file_name.replace('.apk', '')
        plugin_obj = apk.Apk(file_name, '1.00', self.current_time, 'plugin', pkg_name.lower())
        return plugin_obj

    # 创建平台模块的对象并返回
    def create_platform_config(self, file_name):
        pkg_name = self.pkg_prefix + file_name.replace('.apk', '')
        platform_obj = apk.Apk(file_name, '1.00', self.current_time, 'platform', pkg_name.lower())
        return platform_obj


# 主界面 设置源路径与目标路径
class App:
    def __init__(self):
        self.auto = AutoRelease()

        self.root = Tk()
        self.root.title('相关配置')
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        height = 106
        width = 400
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)

        self.frm_source = Frame(self.root)
        Label(self.frm_source, text='来源目录').pack(side=LEFT)
        self.et_source_url = Entry(self.frm_source, textvariable=StringVar(value=self.auto.source_path), width=400)
        self.et_source_url.pack(side=RIGHT)
        self.frm_source.pack()

        self.frm_target = Frame(self.root)
        Label(self.frm_target, text='目标目录').pack(side=LEFT)
        self.et_root_target_url = Entry(self.frm_target, textvariable=StringVar(value=self.auto.root_target_path),
                                        width=400)
        self.et_root_target_url.pack(side=RIGHT)
        self.frm_target.pack()

        self.frm_prefix = Frame(self.root)
        Label(self.frm_prefix, text='包名前缀').pack(side=LEFT)
        self.et_prefix = Entry(self.frm_prefix, textvariable=StringVar(value=self.auto.pkg_prefix), width=400)
        self.et_prefix.pack(side=RIGHT)
        self.frm_prefix.pack()

        self.frm_btn = Frame(self.root)
        self.btn_confirm = Button(self.frm_btn, text='保存', command=self.click_save)
        self.btn_confirm.pack(side=RIGHT)

        self.btn_init = Button(self.frm_btn, text='初始化', command=self.click_init)
        self.btn_init.pack(side=LEFT)

        self.btn_update = Button(self.frm_btn, text='更新', command=self.click_update)
        self.btn_update.pack()
        self.frm_btn.pack()

        self.root.mainloop()

    # 保存配置参数
    def click_save(self):
        source_path = self.et_source_url.get()
        target_path = self.et_root_target_url.get()
        prefix = self.et_prefix.get()
        self.auto.source_path = source_path
        self.auto.root_target_path = target_path
        self.auto.pkg_prefix = prefix
        with open('./config_data.txt', 'w') as data:
            data.write('source_path#' + source_path)
            data.write('\n')
            data.write('target_path#' + target_path)
            data.write('\n')
            data.write('pkg_prefix#' + prefix)

        msgbox.showinfo('提示', '保存成功')

    # 初始化目标路径目录
    def click_init(self):
        self.auto.init_directories()
        msgbox.showinfo('提示', '初始化成功')

    # 更新配置文件
    def click_update(self):
        self.auto.update_config()
        msgbox.showinfo('提示', '更新配置文件成功')


if __name__ == '__main__':
    app = App()
