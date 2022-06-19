import time
from elasticsearch import Elasticsearch
from pyspark.sql.session import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from elasticsearch import Elasticsearch
from sparknlp.annotator import *
from sparknlp.base import *


elastic_host="http://elasticsearch:9200"
elastic_index="taptweet"
kafkaServer="kafkaServer:9092"
topic = "tap"

mapping_principale = {
    "mappings": {
        "properties": 
            {
                "tweet": {"type": "text","fielddata": True},
                "prediction": {"type": "integer","fielddata": True},
                "rating": {"type": "integer","fielddata": True},
                "title": {"type": "text","fielddata": True},
                "product": {"type": "text","fielddata": True},
                "valutazione": {"type": "text","fielddata": True},
                "date": {"type": "date","format": "yyyy-MM-dd"},
                "tokens": {"type": "text","fielddata": True},
                "country": {"type": "text","fielddata": True},
                "verified": {"type": "text","fielddata": True}
            }
    }
}

mapping_secondario = {
    "mappings": {
        "properties": 
            {
                "token": {"type": "text","fielddata": True},
                "result": {"type": "text","fielddata": True}
            }
    }
}


es = Elasticsearch(hosts=elastic_host)
time.sleep(60)
response = es.options(ignore_status=[400], retry_on_timeout=True, request_timeout=60).indices.create(index="principale", mappings=mapping_principale)
response = es.options(ignore_status=[400], retry_on_timeout=True, request_timeout=60).indices.create(index="secondario", mappings=mapping_secondario)

#Kafka Schema
tweetKafka = tp.StructType([
    tp.StructField(name= 'rating', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'title', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'product', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'tweet', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'date', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'country', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'verified', dataType= tp.StringType(),  nullable= True)
])

spark = SparkSession.builder \
    .appName("Spark NLP")\
    .master("local[1]")\
    .config("spark.driver.maxResultSize", "0") \
    .config("spark.driver.memory","6G")\
    .config("spark.kryoserializer.buffer.max", "2000M")\
    .config("es.nodes", "elasticsearch")\
    .config("es.port", "9200")\
    .getOrCreate()

#.config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:3.4.4")\
#.config("spark.executor.memory", "6g")\
# .config("spark.streaming.concurrentJobs","2") \

df_kafka = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .load()

# Cast the message received from kafka with the provided schema
df_kafka = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(F.from_json("value", tweetKafka).alias("data")) \
    .select("data.*")

#PRIMA PIPELINE
document_assembler = DocumentAssembler() \
    .setInputCol('tweet') \
    .setOutputCol('document')
tokenizer = Tokenizer() \
    .setInputCols(['document']) \
    .setOutputCol('token')
sequenceClassifier = DistilBertForSequenceClassification \
      .load("/opt/tap/essentials/distilbert_base_sequence_classifier_amazon_polarity_en_3.3.3_3.0_1637503776952") \
      .setInputCols(['token', 'document']) \
      .setOutputCol('class') \
      .setCaseSensitive(True) \
      .setMaxSentenceLength(512)
pipeline_principale = Pipeline(stages=[document_assembler, tokenizer, sequenceClassifier])

#SECONDA PIPELINE
pos = PerceptronModel.load("/opt/tap/essentials/pos_anc_en_3.0.0_3.0_1614962126490")\
        .setInputCols("document", "token")\
        .setOutputCol("pos")
pipeline_secondaria = Pipeline(stages = [document_assembler, tokenizer, pos])



#PRIMO
df_base = pipeline_principale.fit(df_kafka).transform(df_kafka).select("rating", "title", "product", "tweet", "date", "country", "verified", "class", "token")
df = df_base.withColumn("valutazione", F.col("class.result"))
df = df.withColumn("tokens", F.col("token.result"))
df_principale = df.drop("class", "token")

#SECONDO
result = pipeline_secondaria.fit(df_base).transform(df_base)
result = result.select(F.col("token.result").alias("token"), F.col("pos.result").alias("result"))
result = result.select(F.explode(F.arrays_zip('token', 'result')).alias("cols"))
df_secondario = result.select("cols.token", "cols.result")

#Write the stream to elasticsearch
df_secondario.writeStream \
    .option("checkpointLocation", "/save/location2") \
    .format("es") \
    .start("secondario")

df_principale.writeStream \
    .option("checkpointLocation", "/save/location1") \
    .format("es") \
    .start("principale")

spark.streams.awaitAnyTermination()

