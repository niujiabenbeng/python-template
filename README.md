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
