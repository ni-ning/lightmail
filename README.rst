################################
Send Email for Python
################################



**********
功能特性
**********

对 Python 内置模块 email 和 smtplib 的简单封装


********
安装
********

目前 lightmail 支持的 Python 环境有 2.7, 3.4, 3.5, 3.6, 3.7


为了简化安装过程，推荐使用 pip 进行安装

.. code-block:: bash

    pip install lightmail

升级 lightmail 到新版本::

    pip install -U lightmail

如果需要安装 GitHub 上最新代码::

    pip install https://github.com/ni-ning/lightmail/archive/master.zip



********
使用
********

首先需要配置文件 lightmail.cfg, 文件模板可参考 sample.cfg, 配置文件查找路径为

+ 工程当前目录
+ 运行环境家目录
+ 配置目录 etc


使用案例::

    from lightmail import send_email

    params = {
        "to": "linda@gmail.com",
        "title": "TESTING",
        "content": "Hello Python",
        "attach": ["@/tmp/test.txt"]
    }
    send_email(**params)

