from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
from src.bookdata import Bookdata
from src.user import User

if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("ALSExample") \
        .getOrCreate()

    lines = spark.read.option("header", "true").csv("../BX-CSV_Dump/BX-Book-ratings.csv").rdd

    ratingsRDD = lines.map(lambda p: Row(userId=int(p[0]), bookId=int(p[1]), rating=float(p[2])))

    ratings = spark.createDataFrame(ratingsRDD)

    (training, test) = ratings.randomSplit([0.8, 0.2])

    als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="bookId", ratingCol="rating",
              coldStartStrategy="drop")
    model = als.fit(training)

    predictions = model.transform(test)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print("Root-mean-square error = " + str(rmse))

    userRecs = model.recommendForAllUsers(10)

    user = userRecs.filter(userRecs['userId'] == User._id).collect()

    spark.stop()

    ml = Bookdata()
    ml.loadBookLatestSmall()

    for row in user:
        for rec in row.recommendations:
            print(ml.getBookName(rec.bookId))