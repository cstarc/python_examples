
# 需求

1. 前台展示图片                                                                    done
2. 前台每天自动更新图片，可手动更新
3. 可配置：数据源，解析脚本，图片目录，自动更新时间，限制图片数；可上传脚本
4. 图片每次更新删除，保留标记图片，数据库存储。
5. home修改：分类，不同爬取网站区分

# 概述

目前只能在spider_jpg 目录下执行

## 目录文件说明

- static/ 存放一些静态文件，css，js，images等
- templates/ 存放html
- tmp/ 无用
- server.py 网页，每天调用spider_ht库爬取图片放入static/images ,然后通过web浏览
- spider_ht.py  爬取库

# code

 html 中通过Jinja与flask建立联系

# 参考

1. [Jinja](http://docs.jinkan.org/docs/jinja2/templates.html#for)
