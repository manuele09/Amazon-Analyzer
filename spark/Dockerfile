FROM openjdk:11-jre
ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.2.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH


ADD setup/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz /opt

RUN apt-get update && apt-get -y install bash python3 python3-pip netcat

RUN pip3 install pyspark numpy elasticsearch requests spark-nlp==3.4.4

RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop3.2 ${SPARK_DIR} 
ADD code/nothing.py  /opt/tap/code/nothing.py
RUN $SPARK_DIR/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0,com.johnsnowlabs.nlp:spark-nlp_2.12:3.4.4 /opt/tap/code/nothing.py


ADD code/*  /opt/tap/code/
ADD models /opt/tap/models/
CMD $SPARK_DIR/bin/spark-submit --driver-java-options -Dorg.bytedeco.javacpp.maxphysicalbytes=0 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0,com.johnsnowlabs.nlp:spark-nlp_2.12:3.4.4 /opt/tap/code/amazon_stream_elastic_nml.py
    