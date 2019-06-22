#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: 2015 Jingyi Xiao
# FileName: als.py
# Date: 2016 2016年01月05日 星期二 13时39分19秒
# Encoding: utf-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Note: This source file is NOT a freeware

__author__="Jingyi"

import os, sys, time
import numpy as np
from math import sqrt
from operator import add
from pyspark import SparkConf, SparkContext
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel

sys.path.append("/datas/lib/py")

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class als(object):
    def __init__(self, conf):
        print conf
        self.conf = {}
        self.conf["mem"] = '512m'
        if conf.keys():
            self.conf = conf
            if not self.conf.has_key("mem"):
                self.conf["mem"] = '512m'
        if not self.conf.has_key("parallelize"):
            self.conf["parallelize"] = 8
        if not self.conf.has_key("val"):
            self.conf["val"] = 1
        if self.conf.has_key("sc"):
            self.sc = self.conf['sc']
            print "use exist sc"
        else:
            print "use new sc"
            conf = SparkConf().setAppName("ALS") \
                    .set("spark.executor.memory", self.conf["mem"]) \
                    .set('spark.driver.allowMultipleContexts' , "true")
            self.sc = SparkContext(conf=conf)
        self.sc.setCheckpointDir("/spark/checkpoint")

        self.myRatings = False
        self.ratings = False
        self.objs = False
    
    def ratingData(self):
        # each line: [voterId, objId, score]
        return

    def objData(self):
        # each line: [objId, name]
        return

    def miniRatingData(self):
        # each line: [voterId, objId, score]
        return

    def afterTrain(self, model):
        return

    def loadRating(self):
        self.ratings = self.ratingData()
        return self.ratings

    def loadObj(self):
        self.objs = dict(self.objData())
        return self.objs

    def loadMini(self):
        self.myRatings = self.miniRatingData()
        return self.myRatings

    def prepareTraining(self):
        numPartitions = self.conf["parallelize"]
        self.loadRating()
        ratingsRDD = self.sc.parallelize(self.ratings, numPartitions)
        #objIds = map(lambda x: x[1][1], self.ratings)
        objIds = set(map(lambda x: x[1][1], self.ratings))
        raterIds = set(map(lambda x: x[1][0], self.ratings))
        print "objects, raters number: ",
        print len(objIds), len(raterIds)

        self.loadObj()

        self.loadMini()
        train_per = 10 - self.conf["val"]
        if self.myRatings:
            myRatingsRDD = self.sc.parallelize(self.myRatings, numPartitions)
            training = ratingsRDD.filter(lambda x: x[0] < train_per) \
                    .values().union(myRatingsRDD) \
                    .repartition(numPartitions).cache()
        else:
            training = ratingsRDD.filter(lambda x: x[0] < train_per) \
                    .values().repartition(numPartitions).cache()
        val = ratingsRDD.filter(lambda x: x[0] >= train_per) \
                .values().repartition(numPartitions).cache()

        print "tain: %d, val: %d" % (training.count(), val.count())
#        print training.collect()
        #training.unpersist()
        #val.unpersist()
        return training, val

    def train(self, rank, numIter, lmbda, istest=False, isimp=False, alpha=0.1):
        training, val = self.prepareTraining()
        if self.conf.has_key("model"):
            model = self.loadModel()
        else: 
            if not isimp:
                print "use ALS.train"
                model = ALS.train(training, rank, \
                        iterations=numIter, lambda_=lmbda, \
                        blocks=self.conf["parallelize"], \
                        seed=0, nonnegative=False
                        )
            else:
                print "use ALS.trainImplicit"
                model = ALS.trainImplicit(training, rank, \
                        iterations=numIter, lambda_=lmbda, \
                        blocks=self.conf["parallelize"], seed=0, \
                        alpha=alpha, nonnegative=False \
                        )
            if True:
                os.system("rm -rf cachem")
                model.save(self.sc, "cachem")
                print "saved model"
        if istest:
            self.mkTest(model, val)
        self.afterTrain(model)
        return model, val

    def close(self):
        self.sc.stop()

    def loadModel(self):
        cache_path = "cachem"
        if self.conf.has_key("model"):
            cache_path = self.conf['model']
        model = MatrixFactorizationModel.load(self.sc, cache_path)
        model.userFeatures().repartition(self.conf['parallelize']).cache();
        model.productFeatures().repartition(self.conf['parallelize']).cache();
        print "features:"
        print model.userFeatures().count()
        print model.productFeatures().count()
        print "model loaded"
        return model

    def getRecAll(self, model, num=10, isProduct=True):
        start_t = time.time()

        if isProduct:
            recommendations = model.recommendProductsForUsers(num)
        else:
            recommendations = model.recommendUsersForProducts(num)
        res = recommendations.collect()
        end_t = time.time()
        print "used time: %fs" % (end_t - start_t)
        return res

    def getRecTop(self, model, id, num, isProduct=True):
        print "rec: %d, %d, %d" % (id, num, int(isProduct))
        start_t = time.time()

        try:
            if isProduct:
                recommendations = model.recommendProducts(id, num)
            else:
                recommendations = model.recommendUsers(id, num)
        except:
            recommendations = []
        print len(recommendations)
        end_t = time.time()
        print "used time: %fs" % (end_t - start_t)
        return recommendations

    def getRec(self, model, prating, uid=0):
        start_t = time.time()
        if not self.objs:
            self.loadObj()
        myRatedObjs = set([x[1] for x in prating])
        candidates = self.sc.parallelize([m for m in self.objs if m not in myRatedObjs], self.conf["parallelize"]).cache()
        candidates.count()
        predictions = model.predictAll(candidates.map(lambda x: (uid, x))).collect()
        recommendations = sorted(predictions, key=lambda x: x[2], reverse=True)
        end_t = time.time()
        print "rec used time: %fs" % (end_t - start_t)
        return recommendations

    def getRmse(self, model, val):
        print "RMSE: %f" % self.computeRmse(model, val, val.count())
        return

    def mkTest(self, model, val):
        recommendations = self.getRec(model, self.myRatings)[0:100]
        try:
            lastIds = np.load("rec.npy")
        except:
            lastIds = set([])
        crrIds = set(map(lambda x: x[1], [i for i in recommendations]))
        print "Same as last one: %d" % len(crrIds & lastIds)
        np.save("rec.npy", crrIds)

        self.getRmse(model, val)
        print "Recommended for you:"
        for i in xrange(len(recommendations)):
            print ("%2d: %s" % (i + 1, self.objs[recommendations[i][1]]))

        return recommendations

    def computeRmse(self, model, data, n): 
        if n <= 0:
            return
        predictions = model.predictAll(data.map(lambda x: (x[0], x[1])))
        predictionsAndRatings = predictions.map(lambda x: ((x[0], x[1]), x[2])) \
                .join(data.map(lambda x: ((x[0], x[1]), x[2]))) \
                .values()
        return sqrt(predictionsAndRatings.map(lambda x: (x[0] - x[1]) ** 2).reduce(add) / float(n))

    def testPrint(self):
        print "Hello World!"

def main():
    conf = {}
    t = als(conf)
    t.testPrint()
    return

if __name__ == "__main__":
    main()

# Modeline for ViM {{{
# vim:set ts=4:
# vim600:fdm=marker fdl=0 fdc=3:
# }}}

