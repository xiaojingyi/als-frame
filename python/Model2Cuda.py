#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: Model2Cuda.py
# Date: 2016 2016年01月21日 星期四 22时24分32秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
import gnumpy as gnp
import numpy as np
sys.path.append("/datas/lib/py")
from lib.Util import *
from lib.MyThread import WorkerManager

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class Model2Cuda(object):
    def __init__(self, conf):
        self.conf = {}
        self.conf = conf
        self.avgInit()

    def avgInit(self):
        self.avg = 0
        self.i = 0
        self.sum = 0
    
    def loadData(self):
        print "loadData..."
        product = jsonFileLoad("memtmp/product.json")
        self.productId = map(lambda x: x[0], product)
        self.productFeature = gnp.garray(map(lambda x: x[1], product))
        self.productLen = len(product)
        print "product loaded mem"

        user = jsonFileLoad("memtmp/user.json")
        self.userId = map(lambda x: x[0], user)
        self.userFeature = gnp.garray(map(lambda x: x[1], user))
        self.userLen = len(user)
        print "user loaded mem"

    def recProducts(self, num, offset, limit):
        res = self.recCalc(
                self.productFeature.transpose(),
                self.userFeature,
                num,
                self.productId,
                self.userId,
                offset,
                limit
                )
        return res

    def recUsers(self, num, offset, limit):
        res = self.recCalc(
                self.userFeature.transpose(),
                self.productFeature,
                num,
                self.userId,
                self.productId,
                offset,
                limit
                )
        return res

    def recCalc(self, mat, matSlice, num, idMat, idMatS, offset, limit):
        print offset, limit
        t = time.time()
        s = matSlice[offset: offset+limit]
        f = s.dot(mat)
        res = []
        for i in range(len(f)):
            tmp = self.getOneCalc(f[i], num, idMat)
            res.append([idMatS[i+offset], tmp])
        t_e = time.time()
        t_len = t_e - t
        t_avg = t_len / limit
        print t_len, "s", t_avg, "s"
        return res

    def getOneCalc(self, f, num, idMat):
        t = time.time()
        # prepare start
        #print "begin"
        for i in [0,1,2,3,4,5,6,7,8,9]:
            theta = 1.0 - 1.0*i/10
            f_bool = f > theta
            if f_bool.sum() > num:
                break
        f = f.as_numpy_array()
        f_bool = f_bool.as_numpy_array(dtype=np.bool)
        #print time.time() - t
        f_args = np.argwhere(f_bool == True)
        #print f_args.shape
        f_args = f_args.reshape(len(f_args)).tolist()
        #print time.time() - t
        # prepare end

        # load real id
        res = map(lambda x: [idMat[x], f[x]], f_args)
        #print f_bool.shape, len(res)

        # sort
        res_sort = sorted(res, key=lambda x: x[1], reverse=True)
        return res_sort[0: num]

    def testPrint(self):
        print self.sum, self.i, self.avg

    # backup used
    def recProduct(self, userIndex, num):
        print "recProduct...", userIndex
        t = time.time()
        u = self.userFeature[userIndex]
        f = u.dot(self.productFeature.transpose())
        for i in [0,1,2,3,4,5,6,7,8,9]:
            theta = 1.0 - 1.0*i/10
            f_bool = f > theta
            if f_bool.sum() > num:
                break
        f = f.as_numpy_array()
        f_bool = f_bool.as_numpy_array(dtype=np.bool)
        f_args = np.argwhere(f_bool == True)
        f_args = f_args.reshape(len(f_args)).tolist()
        print time.time() - t, "s"
        # prepare end

        res = map(lambda x: [self.productId[x], f[x]], f_args)
        print len(res)
        res_sort = sorted(res, key=lambda x: x[0], reverse=True)

        t_c = time.time() - t
        self.sum += t_c
        self.i += 1
        self.avg = self.sum / self.i
        return self.userId[userIndex], res_sort[0: num]

def mkModelDatas(param):
    t = param[0]
    fnamePreffix = param[1]
    rec_t = param[2]
    itemLen = 300
    recLen = 100
    datas = {}
    length = t.userLen
    if rec_t == "user":
        length = t.productLen
    for i in range(length/itemLen):
        if rec_t == "product":
            res = t.recProducts(recLen, i*itemLen, itemLen)
        elif rec_t == "user":
            res = t.recUsers(recLen, i*itemLen, itemLen)
        else:
            print "err"
            return

        for one in res:
            id = one[0]
            rec = one[1]
            datas[id] = rec

        if i % 100 == 0:
            print rec_t, i, "saved"
            fname = "%s_%d.json"%(fnamePreffix, i)
            jsonFileSave(fname, datas)
            datas = {}
    t.testPrint()
    jsonFileSave("%s_end.json"%fnamePreffix, datas)
    t.avgInit()
    return

def main():
    conf = {}
    t = Model2Cuda(conf)
    t.loadData()

    wm = WorkerManager(2)
    param = [t, "datas/productUsers", "user"]
    wm.add_job(mkModelDatas, [param])

    param = [t, "datas/userProducts", "product"]
    mkModelDatas(param)

    wm.wait_for_complete()
    return

    userProducts = {}
    productUsers = {}
    itemLen = 300
    recLen = 100
    if sys.argv[1] == 'product':
        for i in range(t.userLen/itemLen):
            res = t.recProducts(recLen, i*itemLen, itemLen)
            for one in res:
                id = one[0]
                rec = one[1]
                userProducts[id] = rec
            if i % 100 == 0:
                jsonFileSave("datas/userProducts_%d.json"%i, userProducts)
                userProducts = {}
        t.testPrint()
        jsonFileSave("datas/userProducts_end.json", userProducts)
        t.avgInit()
    elif sys.argv[1] == "user":
        for i in range(t.productLen/itemLen):
            res = t.recUsers(recLen, i*itemLen, itemLen)
            for one in res:
                id = one[0]
                rec = one[1]
                productUsers[id] = rec
            if i % 100 == 0:
                jsonFileSave("datas/productUsers_%d.json"%i, productUsers)
                productUsers = {}
        t.testPrint()
        jsonFileSave("datas/productUsers_end.json", productUsers)
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

