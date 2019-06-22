#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: AbsData.py
# Date: 2016 2016年01月05日 星期二 13时37分36秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
sys.path.append("/datas/lib/py")

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class AbsData(object):
    def __init__(self, conf):
        self.conf = {}
        self.conf = conf
    
    def testPrint(self):
        print "Hello World!"

def main():
    conf = {}
    t = AbsData(conf)
    t.testPrint()
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

