# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: db_client.py
# @time: 2023/7/22 12:46
from elasticsearch import Elasticsearch
from pymilvus import connections, Collection

# 连接Elasticsearch
es_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# 连接Milvus
connections.connect("default", host="localhost", port="19530")
milvus_client = Collection("docs_qa")
