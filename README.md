# Amazon Analyzer

## Dipendenze da scaricare
Inserire [Kafka](https://archive.apache.org/dist/kafka/3.1.0/kafka_2.13-3.1.0.tgz)
in Amazon-Analyzer/kafka/setup

Inserire [Spark](https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz)
in Amazon-Analyzer/spark/setup

Moduli per Spark NLP: 
[1](https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/models/distilbert_base_sequence_classifier_amazon_polarity_en_3.3.3_3.0_1637503776952.zip)
, 
[2](https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/models/pos_anc_en_3.0.0_3.0_1614962126490.zip)
, da inserire in Amazon-Analyzer/spark/modules_nlp

## Per eseguire
```bash
docker compose up
```
## Link Utili

| Server                                                       | Porta                            |
| ------------------------------------------------------------ | -------------------------------- |
| [Kafka](http://localhost:8080) | 8080|
| [Spark](http://localhost:4040) | 4040|
| [ElasticSearch](http://localhost:9200) | 9200   |
| [Kibana](http://localhost:5601) | 5601    |




