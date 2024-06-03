import pandas
from langchain.schema import Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.schema import BaseRetriever
from typing import Any, List


def get_cfn_outputs(stackname, cfn):
    outputs = {}
    for output in cfn.describe_stacks(StackName=stackname)["Stacks"][0]["Outputs"]:
        outputs[output["OutputKey"]] = output["OutputValue"]
    return outputs


def keyword_search(index_name, query_text, aos_client, model_id):
    query = {
        "size": 10,
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["text"],
            }
        },
    }

    res = aos_client.search(index=index_name, body=query)

    query_result = []
    result_docs = []
    for hit in res["hits"]["hits"]:
        row = [
            hit["_id"],
            hit["_score"],
            hit["_source"]["title"],
            hit["_source"]["text"],
            hit["_source"]["genre"],
            hit["_source"]["rating"],
        ]
        query_result.append(row)

        metadata = {"score": hit["_score"], "id": hit["_id"]}

        content = {
            "title": hit["_source"]["title"],
            "genre": hit["_source"]["genre"],
            "rating": hit["_source"]["rating"],
            "text": hit["_source"]["text"],
        }

        doc = Document(page_content=json.dumps(content, ensure_ascii=False), metadata=metadata)
        result_docs.append(doc)

    query_result_df = pd.DataFrame(
        data=query_result, columns=["_id", "_score", "title", "plot", "genre", "rating"]
    )
    display(query_result_df)
    return result_docs


def semantic_search(index_name, query_text, aos_client, model_id):
    query = {
        "size": 10,
        "_source": {"excludes": ["vector_field"]},
        "query": {
            "neural": {"vector_field": {"query_text": query_text, "model_id": model_id, "k": 30}},
        },
    }

    res = aos_client.search(index=index_name, body=query)

    query_result = []
    for hit in res["hits"]["hits"]:
        row = [
            hit["_id"],
            hit["_score"],
            hit["_source"]["title"],
            hit["_source"]["text"],
            hit["_source"]["genre"],
            hit["_source"]["rating"],
        ]
        query_result.append(row)

        metadata = {"score": hit["_score"], "id": hit["_id"]}

        content = {
            "title": hit["_source"]["title"],
            "genre": hit["_source"]["genre"],
            "rating": hit["_source"]["rating"],
            "text": hit["_source"]["text"],
        }

        doc = Document(page_content=json.dumps(content, ensure_ascii=False), metadata=metadata)
        result_docs.append(doc)

    query_result_df = pd.DataFrame(
        data=query_result, columns=["_id", "_score", "title", "plot", "genre", "rating"]
    )
    display(query_result_df)
    return result_docs


def hybrid_search(index_name, query_text, aos_client, model_id):
    query = {
        "size": 10,
        "_source": {"exclude": ["vector_field"]},
        "query": {
            "hybrid": {
                "queries": [
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["title", "text", "genre"],
                        }
                    },
                    {
                        "neural": {
                            "vector_field": {
                                "query_text": query_text,
                                "model_id": model_id,
                                "k": 30,
                            }
                        }
                    },
                ]
            }
        },
        "search_pipeline": {
            "description": "Post processor for hybrid search",
            "phase_results_processors": [
                {
                    "normalization-processor": {
                        "normalization": {"technique": "min_max"},
                        "combination": {
                            "technique": "arithmetic_mean",
                            "parameters": {"weights": [0.3, 0.7]},
                        },
                    }
                }
            ],
        },
    }

    res = aos_client.search(index=index_name, body=query)

    query_result = []
    for hit in res["hits"]["hits"]:
        row = [
            hit["_id"],
            hit["_score"],
            hit["_source"]["title"],
            hit["_source"]["text"],
            hit["_source"]["genre"],
            hit["_source"]["rating"],
        ]
        query_result.append(row)

        metadata = {"score": hit["_score"], "id": hit["_id"]}

        content = {
            "title": hit["_source"]["title"],
            "genre": hit["_source"]["genre"],
            "rating": hit["_source"]["rating"],
            "text": hit["_source"]["text"],
        }

        doc = Document(page_content=json.dumps(content, ensure_ascii=False), metadata=metadata)
        result_docs.append(doc)

    query_result_df = pd.DataFrame(
        data=query_result, columns=["_id", "_score", "title", "plot", "genre", "rating"]
    )
    display(query_result_df)
    return result_docs


class OpenSearchLexicalSearchRetriever(BaseRetriever):
    os_client: Any
    index_name: str
    k = 10
    minimum_should_match = 0
    filter = []

    def _reset_search_params(
        self,
    ):

        self.k = 10
        self.minimum_should_match = 0
        self.filter = []

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        body = {
            "size": self.k,
            "_source": {"exclude": ["vector_field"]},
            "query": {
                "hybrid": {
                    "queries": [
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["title", "text", "genre"],
                            }
                        },
                        {
                            "neural": {
                                "vector_field": {
                                    "query_text": query_text,
                                    "model_id": "jK-l048BhWoFUAg8WOdO",
                                    "k": 30,
                                }
                            }
                        },
                    ]
                }
            },
            "search_pipeline": {
                "description": "Post processor for hybrid search",
                "phase_results_processors": [
                    {
                        "normalization-processor": {
                            "normalization": {"technique": "min_max"},
                            "combination": {
                                "technique": "arithmetic_mean",
                                "parameters": {"weights": [0.3, 0.7]},
                            },
                        }
                    }
                ],
            },
        }
        res = self.os_client.search(index=index_name, body=body)

        query_result = []

        for hit in res["hits"]["hits"]:
            metadata = {"score": hit["_score"], "id": hit["_id"]}

            content = {
                "title": hit["_source"]["title"],
                "genre": hit["_source"]["genre"],
                "rating": hit["_source"]["rating"],
                "text": hit["_source"]["text"],
                "score": hit["_score"],
            }

            doc = Document(page_content=json.dumps(content, ensure_ascii=False), metadata=metadata)
            query_result.append(doc)

        return query_result
