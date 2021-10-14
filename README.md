# python工程模板

python的环境配置较为简单. 这里仅仅包含一些常用的工具.

TODO: 重新组织工程布局, 将lib和tools合并, 最终消除init.


### 环境配置

python配置用python-lsp, 目前用的python language server为python-lsp-server.
安装命令: `pip install 'python-lsp-server[all]'`

配置文件:

1. jedi不需要配置文件
2. pylint需要配置文件: .pylintrc
3. yapf需要配置文件: .style.yapf


### pylintrc

pylint的配置文件为:pylintrc. 如果python文件不在module中, 则pylint不会在其父目录
寻找pylintrc, 这里我们通过修改pylint的源码来确保pylint能找到对应的配置文件.
源码位于: `/pylint/config/find_default_config_files.py`
在`find_default_config_files`函数中, 去掉对`__init__.py`的限制即可.

具体实现参考:

``` python
if True:
    curdir = os.path.abspath(os.getcwd())
    while not os.path.samefile(curdir, "/"):
        curdir = os.path.abspath(os.path.join(curdir, ".."))
```


### 检查代码的风格

``` shell
pylint lib tools     # 使用本目录中的.lintrc
yapf -ir lib tools   # 使用本目录中的.style.yapf
```


### 多线程问题

Linux下多线程没问题, Windows下pickle无法打包局部名字空间, 用了dill之后也不行,
这里限制一下, Windows下需要处理的task需要位于全局名字空间.


### 中文字体支持

lib.util.draw_chinese_textlines()方法用的是宋体, 字体文件为simsun.ttc.
Linux系统中, 可以用`fc-list :lang=zh-cn`命令查看当前机器的所有字体.
如果没有simsun.ttc, 则将Windows中对应的文件拷贝到Linux中即可.

Windows文件路径: `C:\Windows\Fonts\simsun.ttc`

Linux文件路径: `/usr/share/fonts/simsun.ttc`


### conda环境新建和库的安装

注意: pytorch和detectron2只能用pip安装, conda远程仓库的版本太老了.

``` shell
conda create --name pytorch

conda install pip protobuf flask oss2

pip install 'python-lsp-server[all]'

pip install opencv-python opencv-contrib-python
```
