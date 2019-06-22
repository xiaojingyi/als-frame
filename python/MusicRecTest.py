#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: MusicRecTest.py
# Date: 2016 2016年01月25日 星期一 18时41分34秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
sys.path.append("/datas/lib/py")
from lib.Util import *
import redis
import json

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class MusicRecTest(object):
    def __init__(self, conf):
        self.conf = {}
        self.conf = conf
        print "initing..."
        self.r = redis.Redis(host='localhost')
        print "inited"
    
    def rec(self, pcode):
        return

    def cache(self):
        prefix = "qiaoqiao:rec:"
        fls = walkDir("datas")
        a = "datas/productUsers_";
        b = "datas/userProducts_";
        lenA = len(a)
        for one in fls:
            tmp = one[0:lenA]
            if tmp == a or tmp == b:
                data = jsonFileLoad(one)
                print one
                for k in data.keys():
                    value = map(lambda x: x[0], data[k])
                    if tmp == a:
                        key = prefix + "p_" + str(k)
                    elif tmp == b:
                        key = prefix + "u_" + str(k)
                    self.r.set(key, json.dumps(value))

        print "done"
        """
        exit()
        self.prec = jsonFileLoad("datas/userProducts.json")
        self.urec = jsonFileLoad("datas/productUsers.json")
        for k in self.prec.keys():
            key = prefix + "p_" + str(k)
            value = map(lambda x: x[0], self.prec[k])
            self.r.set(key, json.dumps(value))
        for k in self.urec.keys():
            key = prefix + "u_" + str(k)
            value = map(lambda x: x[0], self.urec[k])
            self.r.set(key, json.dumps(value))
        """
        return

    def testPrint(self):
        print "Hello World!"

def main():
    conf = {}
    t = MusicRecTest(conf)
    t.cache()
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

