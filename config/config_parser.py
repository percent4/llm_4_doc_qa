# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: config_parser.py
# @time: 2023/9/8 16:49
import os
import yaml


# PROJECT PATH
PROJECT_DIR = os.getenv("PROJECT_PATH", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# basic config parser
with open(os.path.join(PROJECT_DIR, 'config/basic_config.yml'), encoding="utf-8") as yaml_file:
    basic_config = yaml.safe_load(yaml_file)

PROJECT_NAME = basic_config['project']

server_config = basic_config['server']
SERVER_HOST = server_config.get("host", "127.0.0.1")
SERVER_PORT = server_config.get("port", 80)

log_config = basic_config['log']
LOG_PATH = log_config.get('save_path', 'logs')

langchain_config = basic_config["langchain"]
CHUNK_SIZE = langchain_config.get("chunk_size", 100)
SYSTEM_ROLE = langchain_config.get("system_role", "")

retrieval_config = basic_config["retrieval"]
MILVUS_SIZE = retrieval_config.get("milvus_size", 2)
MILVUS_THRESHOLD = retrieval_config.get("milvus_threshold", 2)
ES_SIZE = retrieval_config.get("es_size", 2)
RERANK_TOP_N = retrieval_config.get("rerank_top_n", 5)

# basic config parser
with open(os.path.join(PROJECT_DIR, 'config/model_config.yml'), encoding="utf-8") as yaml_file:
    model_config = yaml.safe_load(yaml_file)

models = model_config['models']
MODEL_NAME_LIST = models.get("name", [])
EMBEDDING_MODEL = MODEL_NAME_LIST[0]
EMBEDDING_API = models.get("embedding_api", "")
CHAT_COMPLETION_API = models.get("chat_completion_api", "")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_API = models.get("openai_embedding_api", "")
OPENAI_CHAT_COMPLETION_API = models.get("openai_chat_completion_api", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
