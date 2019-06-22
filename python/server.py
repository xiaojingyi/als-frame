#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: server.py
# Date: 2016 2016年01月11日 星期一 12时58分08秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
import web
import json
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import shutil
import random
sys.path.append("/datas/lib/py")
from lib.Util import *   
from lib.MyThread import WorkerManager
from AlsTest import AlsTest

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

global rec, g_model, g_val
rec = AlsTest({})
g_model, g_val = rec.train(12, 20, 5.0, True)

class MyHttpHandler(BaseHTTPRequestHandler):
    def dataBack(self, strs):
        strs = json.dumps(strs)
        enc="UTF-8"
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(strs)))
        self.end_headers() 
        self.wfile.write(strs)

    def do_GET(self):
        global rec, g_model, g_val
        recIds = rec.getRec(g_model, rec.myRatings)

        self.dataBack(recIds)
        return 

def main():
    httpd=HTTPServer(('',1231),MyHttpHandler)
    httpd.serve_forever()
    """
    wm = WorkerManager(3)
    wm.add_job(calc, [1]) 
    wm.wait_for_complete()
    """
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

