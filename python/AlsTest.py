#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: AlsTest.py
# Date: 2016 2016年01月05日 星期二 15时57分14秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
sys.path.append("/datas/lib/py")
from als import als
import sys
import itertools
from math import sqrt
from operator import add
from os.path import join, isfile, dirname

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class AlsTest(als):
    def __init__(self, conf):
        self.datapath = "/usr/local/sparkpkg/data/movielens/medium/"
        self.minipath = "/usr/local/sparkpkg/machine-learning/personalRatings.txt"
        super(AlsTest, self).__init__(conf)
    
    def parseRating(self, line):
        fields = line.strip().split("::")
        return long(fields[3]) % 10, (int(fields[0]), int(fields[1]), float(fields[2]))

    def parseMovie(self, line):
        fields = line.strip().split("::")
        return int(fields[0]), fields[1]

    def loadRatings(self, ratingsFile, isall=False):
        if not isfile(ratingsFile):
            print "File %s does not exist." % ratingsFile
            sys.exit(1)
        f = open(ratingsFile, 'r')
        if not isall:
            ratings = filter(lambda r: r[2] > 0, [self.parseRating(line)[1] for line in f])
        else:
            ratings = [self.parseRating(line) for line in f]
        f.close()
        if not ratings:
            print "No ratings provided."
            sys.exit(1)
        else:
            return ratings

    def ratingData(self):
        data = self.loadRatings(self.datapath + "ratings.dat", True)
        return data

    def objData(self):
        f = open(self.datapath + "movies.dat", 'r')
        objs = [self.parseMovie(line) for line in f]
        return objs

    def miniRatingData(self):
        ratings = self.loadRatings(self.minipath)
        return ratings

    def testPrint(self):
        print "Hello World!"

def main():
    if len(sys.argv) > 1:
        t = AlsTest({"mem": "1g", "model": 1})
        model = t.loadModel()
        #t.loadMini()
        #print t.getRec(model, t.myRatings)
        t.train(12, 20, 1.0, True)
        #for i in range(100):
        #    t.getRec(model, t.myRatings)
    else:
        t = AlsTest({"mem": "16g"})
        t.train(30, 20, 0.1, False)
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

