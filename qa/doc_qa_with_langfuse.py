# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: doc_qa_with_langfuse.py
# @time: 2025/3/17 20:05
# @desc: document qa with langfuse tracing
import os
import cohere
from uuid import uuid4
from dotenv import load_dotenv
from openai import OpenAI
from langfuse import Langfuse
from operator import itemgetter

from utils.db_client import es_client, milvus_client

load_dotenv('../config/.env')

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
    host=os.getenv("LANGFUSE_HOST", ""),
)


class DocumentQA(object):
    def __init__(self, query):
        self.query = query
        self.trace = self.init_langfuse_trace()

    def init_langfuse_trace(self):
        trace_id = str(uuid4())
        print(f"trace_id: {trace_id}")
        trace = langfuse.trace(
            name="RAG Pipeline",
            user_id="user_123",
            id=trace_id
        )
        trace.span(
            name="User Query",
            input=self.query,
        )
        return trace

    # ES检索
    def _es_retrieval(self):
        result = []
        # 查询数据(全文搜索)
        dsl = {
            'query': {
                'match': {
                    'content': self.query
                }
            },
            "size": 5
        }
        search_result = es_client.search(index='docs', body=dsl)
        if search_result['hits']['hits']:
            result = [
                {
                    "content": hit['_source']['content'],
                    "source": hit['_source']['source']
                }
                for hit in search_result['hits']['hits']
            ]
        self.trace.span(
            name="ES Retrieval",
            input=self.query,
            output=result
        )
        return result

    # get text embedding
    def _get_text_embedding(self):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        embedding = client.embeddings.create(
            model="text-embedding-ada-002",
            input=self.query
        )
        self.trace.generation(
            name="OpenAI Text Embedding",
            model="text-embedding-ada-002",
            input=self.query,
            output=len(embedding.data[0].embedding),
            usage_details=embedding.usage
        )
        return embedding.data[0].embedding

    # Milvus检索
    def _milvus_retrieval(self):
        # milvus search content
        vectors_to_search = [self._get_text_embedding()]
        # 通过嵌入向量相似度获取相似文本
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 5},
        }
        result = milvus_client.search(vectors_to_search,
                                      "embeddings",
                                      search_params,
                                      limit=5,
                                      output_fields=["text", "source"])
        # filter by similarity score
        result = [
            {
                "content": _.entity.get('text'),
                "source": _.entity.get('source'),
                "score": dist
            }
            for _, dist in zip(result[0], result[0].distances) if dist > 0.5
        ]
        self.trace.span(
            name="Milvus Retrieval",
            input=self.query,
            output=result
        )
        return result

    @staticmethod
    # sort the es and milvus retrieval results by rrf
    def retrieval(
            es_result: list[dict],
            milvus_result: list[dict]
    ) -> list[dict[str, float]]:
        """
        Sort the ES and Milvus retrieval results by RRF.
        :param es_result: list of ES retrieval result
        :param milvus_result: list of Milvus retrieval result
        :return:
        """
        es_result = [_["content"] for _ in es_result]
        milvus_result = [_["content"] for _ in milvus_result]
        doc_lists = [es_result, milvus_result]
        # Create a union of all unique documents in the input doc_lists
        all_documents = set()
        for doc_list in doc_lists:
            for doc in doc_list:
                all_documents.add(doc)

        # Initialize the RRF score dictionary for each document
        rrf_score_dic = {doc: 0.0 for doc in all_documents}

        # Calculate RRF scores for each document
        weights = [0.5, 0.5]
        c = 60
        for doc_list, weight in zip(doc_lists, weights):
            for rank, doc in enumerate(doc_list, start=1):
                rrf_score = weight * (1 / (rank + c))
                rrf_score_dic[doc] += rrf_score

        # Sort documents by their RRF scores in descending order
        sorted_documents = sorted(rrf_score_dic.items(), key=itemgetter(1), reverse=True)
        # get top 5 documents
        result = []
        for i in range(len(sorted_documents)):
            text, score = sorted_documents[i]
            result.append({"content": text, "score": score})
        return result

    # rerank by Cohere
    def rerank(self, before_rerank_contents):
        documents = [_["content"] for _ in before_rerank_contents]
        cohere_client = cohere.Client(os.getenv("COHERE_API_KEY", ""))
        results = cohere_client.rerank(model="rerank-multilingual-v2.0",
                                       query=self.query,
                                       documents=documents,
                                       top_n=5)
        after_rerank_contents = []
        for hit in results:
            after_rerank_contents.append({"content": hit.document['text'], "score": hit.relevance_score})
        self.trace.span(
            name="Cohere Rerank",
            input=before_rerank_contents,
            output=after_rerank_contents
        )
        return after_rerank_contents

    # answer by OpenAI
    def answer(self):
        # retrieve
        es_result = self._es_retrieval()
        milvus_result = self._milvus_retrieval()
        before_rerank_contents = self.retrieval(es_result, milvus_result)
        after_rerank_contents = self.rerank(before_rerank_contents)
        # construct prompt
        prompt = "Based on the following documents, answer the question: \n"
        for i, text_dict in enumerate(after_rerank_contents):
            prompt += f"document {i+1}: {text_dict['content']}\n"
        prompt += f"\nHere is the user's question: {self.query}\nPlease answer the question."
        # chat completion
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        max_tokens = 300
        temperature = 0.5
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        response = result.choices[0].message.content
        # langfuse tracing
        self.trace.generation(
            name="OpenAI Generation",
            input=prompt,
            output=response,
            model_parameters={"max_tokens": max_tokens, "temperature": temperature},
            usage_details=result.usage
        )
        return response


if __name__ == '__main__':
    doc_qa = DocumentQA("格里芬发表演讲时说了什么？")
    answer = doc_qa.answer()
    print(answer)
