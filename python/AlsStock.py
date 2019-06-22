#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: AlsStock.py
# Date: 2016 2016年01月12日 星期二 23时13分04秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
sys.path.append("/datas/lib/py")
from als import als
from lib.Util import *
import json

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class AlsStock(als):
    def __init__(self, conf):
        self.datapath = "../../stockcn/data/mat/"
        super(AlsStock, self).__init__(conf)
    
    def loadJson(self, fname):
        fname = self.datapath + fname
        content = getFileContent(fname, False)
        res = json.loads(content)
        return res

    def saveJson(self, fname, data):
        fname = self.datapath + fname
        res = json.dumps(data)
        writeToFile(fname, res)
        return

    def ratingData(self):
        data = self.loadJson("rates.json")
        res = []
        for one in data:
            try:
                res.append([one[0], (int(one[1]), int(one[2]), one[3])])
            except:
                continue
        return res

    def objData(self):
        objs = self.loadJson("obj.json")
        res = {}
        for one in objs.keys():
            res[int(one)] = objs[one]
        return res

    def miniRatingData(self):
        return False

    def loadRaters(self):
        raters = self.loadJson("raters.json")
        return raters

    def recThread(self, param):
        model, raterVotes, raterId = param
        self.getRec(model, raterVotes, raterId)
        return

    def recTop(self, model):
        raters = self.loadRaters()
        stockact = {}
        len_raters = len(raters.keys())
        i = 0
        total = 0
        for rater in raters.keys():
            try:
                raterId = int(rater)
            except:
                print "err: " + rater
                continue
            raterVotes = map(lambda x: [int(x[0]), int(x[1]), x[2]], raters[rater])
            res = self.getRec(model, raterVotes, raterId)
            """
            for one in res:
                code = "%06d" % one[1]
                money = self.toMoney(one[2])
                if money > 0:
                    if stockact.has_key(code):
                        stockact[code]['sum'] += money
                        stockact[code]['count'] += 1
                        stockact[code]['avg'] = stockact[code]['sum'] / stockact[code]['count']
                    else:
                        stockact[code] = {
                                "sum": money,
                                "avg": money,
                                "count": 1
                                }
                    total += money
            """
            print "done: %d/%d" % (i, len_raters)
            i += 1
        print "total amount: %d" % total 
        if total < 0: 
            reverse = False
        reverse = True
        topls = sorted(stockact.iteritems(), key=lambda d:d[1]["avg"], reverse=reverse)
        self.saveJson("stock_analyse.json", topls)
        for i in range(len(topls)):
            print topls[i]
            if i > 100:
                break
        return

    def toMoney(self, score):
        if score == 0:
            return 0
        abs_score = abs(score)
        v = score / abs_score
        str_score = str(abs_score)
        score_arr = str_score.split(".")
        h = int(score_arr[0])
        f = score_arr[1]
        if f[0] == '0':
            f = '1' + f[1:]
        f = f[:1] + '.' + f[1:]
        f = float(f) * (10 ** (h-1))
        return int(f*v/1000000)

    def testPrint(self):
        print "Hello World!"

def main():
    if len(sys.argv) > 1:
        t = AlsStock({
            "mem": "1g", 
            "parallelize": 1, 
            "val": 1,
            "model": "cachem",
            })
        if sys.argv[1] == '1':
            #t.loadMini()
            #print t.getRec(model, t.myRatings)
            model, val = t.train(12, 20, 1.0, False)
            rec_ls = t.getRecAll(model, 5)
            raters = t.loadRaters()
            for one in rec_ls:
                code = "%06d" % one[0]
                rates = one[1]
                objs = set(map(lambda x: x[1], raters[code]))
                #print sorted(objs)
                for one_rate in rates:
                    objId = "%06d" % one_rate[1]
                    #print objId, list(one_rate)
                    if objId in objs:
                        print "in: " + objId
            #for i in range(100):
            #    t.getRec(model, t.myRatings)
        elif sys.argv[1] == '2':
            model = t.loadModel()
            t.recTop(model)
        else:
            print "param error"
    else:
        t = AlsStock({
            "mem": "2g",
            "parallelize": 4,
            "val": 1,
            })
        model, val = t.train(100, 100, 0.3, False)
        t.getRmse(model, val)

    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

