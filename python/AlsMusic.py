#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: AlsMusic.py
# Date: 2016 2016年01月20日 星期三 11时59分19秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
import json
import random
sys.path.append("/datas/lib/py")
from als import als
from lib.Util import *

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class AlsMusic(als):
    def __init__(self, conf):
        print "alsmusic 1.0"
        self.datapath = "../../music_data/datas/"
        super(AlsMusic, self).__init__(conf)
    
    def loadJson(self, fname):
        fname = self.datapath + fname
        content = getFileContent(fname, False)
        res = json.loads(content)
        return res

    def objData(self):
        objs = self.loadJson("objs.json")
        return objs

    def ratingData(self):
        data = self.loadJson("rates.json")
        res = []
        for one in data:
            rand_num = random.randint(0,9)
            res.append([rand_num, (int(one[0]), int(one[1]), one[2])])
        return res

    def recTest(self, model):
        ratings = self.ratingData()
        obj = list(set(map(lambda x: x[1][1], ratings)))
        rater = list(set(map(lambda x: x[1][0], ratings)))
        for one in rater:
            self.getRecTop(model, one, 10)

    def testPrint(self):
        print "Hello next!"

def instant(m="", sc=False):
    conf = {
        "mem": "24g",
        "parallelize": 4,
        "val": 1,
        }
    if m:
        conf["model"] = m
    if sc:
        conf['sc'] = sc
    t = AlsMusic(conf)
    return t

def main():
    if len(sys.argv) > 1:
        t = instant(sys.argv[1])
        model = t.loadModel()
        t.recTest(model)
        #rec_ls = t.getRecAll(model, 1)
        t.recTest()
    else:
        t = instant()
        model, val = t.train(100, 100, 0.1, False, isimp=True, alpha=200000.1)
        t.getRmse(model, val)
        p = model.productFeatures().collect()
        u = model.userFeatures().collect()
        p = map(lambda x: [x[0], list(x[1])], p)
        u = map(lambda x: [x[0], list(x[1])], u)
        jsonFileSave("datas/product.json", p)
        jsonFileSave("datas/user.json", u)
        #rec_ls = t.getRecAll(model, 3)
        #t.recTest(model)
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

