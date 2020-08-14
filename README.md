# python工程模板

python的环境配置较为简单. 这里仅仅包含一些常用的工具.

注意: 用pyls时, 需要切换到装有pyls的python环境, 否则会报找不到所需要的工具.

### 中文字体支持

lib.util.draw_chinese_textlines()方法用的是宋体, 字体文件为simsun.ttc.
Linux系统中, 可以用`fc-list :lang=zh-cn`命令查看当前机器的所有字体.
如果没有simsun.ttc, 则将Windows中对应的文件拷贝到Linux中即可.

Windows文件路径: `C:\Windows\Fonts\simsun.ttc`

Linux文件路径: `/usr/share/fonts/simsun.ttc`
