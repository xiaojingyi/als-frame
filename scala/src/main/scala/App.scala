/**
 * FileName:       App.scala
 * Type:           scala
 * Encoding:       utf-8
 * Copyright:      (c) 2015 Jingyi Xiao
 * Note:           This source file is NOT a freeware
 * Authors:        Jingyi Xiao <kxwarning@126.com>
 * Description:
 */
import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf

object App {
    def main(args: Array[String]) {
        var beg = System.currentTimeMillis()
        var sparkHome = "/usr/local/spark-1.6.0-bin-hadoop2.6/"
        val logFile = sparkHome + "/README.md" // Should be some file on your system
        val conf = new SparkConf().setAppName("test").set("spark.executor.memory", "2g").set("spark.driver.allowMultipleContexts", "true")
        val sc = new SparkContext(conf)
        val sc1 = new SparkContext(conf)
        val logData = sc.textFile(logFile, 1).cache()
        var numAs: Long = 0
        var numBs: Long = 0
        for (i <- 1 to 1000){
            numAs = logData.filter(line => line.contains("a")).count()
            numBs = logData.filter(line => line.contains("b")).count()
        }
        var eeg = System.currentTimeMillis()
        println("end time: %s".format(eeg - beg))
        println("Lines with a: %s, Lines with b: %s".format(numAs, numBs))
    }
}

