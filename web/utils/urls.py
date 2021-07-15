#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/12/6 9:17
# @Author : ma.fei
# @File : urls.py.py
# @Software: PyCharm

from web.urls.user     import user
from web.urls.role     import role
from web.urls.logon    import logon
from web.urls.comm     import comm
from web.urls.main     import main
from web.urls.menu     import menu
from web.urls.func     import func
from web.urls.ds       import ds
from web.urls.server   import server
from web.urls.sql      import sql
from web.urls.wtd      import wtd
from web.urls.backup   import backup
from web.urls.sync     import sync
from web.urls.transfer import transfer
from web.urls.bigdata  import bigdata
from web.urls.port     import port
from web.urls.sys      import sys
from web.urls.archive  import archive
from web.urls.tools    import tools
from web.urls.monitor  import monitor
from web.urls.inst     import inst
from web.urls.slow     import slow
from web.urls.minio    import minio
from web.urls.bbtj    import bbtj


urls = []
urls.extend(logon)
urls.extend(comm)
urls.extend(main)
urls.extend(user)
urls.extend(role)
urls.extend(menu)
urls.extend(func)
urls.extend(ds)
urls.extend(server)
urls.extend(sql)
urls.extend(wtd)
urls.extend(backup)
urls.extend(sync)
urls.extend(transfer)
urls.extend(bigdata)
urls.extend(port)
urls.extend(sys)
urls.extend(archive)
urls.extend(tools)
urls.extend(monitor)
urls.extend(inst)
urls.extend(slow)
urls.extend(minio)
urls.extend(bbtj)