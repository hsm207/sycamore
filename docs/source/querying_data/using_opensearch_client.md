


## Hybrid search

Hybrid Search is implemented as a Search Processor, so in order to use it for the best quality search relevance, we must make a pipeline with both processors

```javascript
PUT /_search/pipeline/<hybrid_rag_pipeline>
{
  "description": "RAG + Hybrid Search Pipeline",
    "phase_results_processors": [
        {
            "normalization-processor": {
                "normalization": {
                    "technique": "min_max"
                },
                "combination": {
                    "technique": "arithmetic_mean",
                    "parameters": {
                        "weights": [.889, .111]
                    }
                }
            }
        }
    ],
    "response_processors": [
        {
            "retrieval_augmented_generation": {
                "tag": "openai_pipeline_demo",
                "description": "Demo pipeline Using OpenAI Connector",
                "model_id": "<openai_id>",
                "context_field_list": ["text"]
            }
        }
    ]
}
```

## Neural search

# Neural Search

The Aryn Conversational Search Stack uses OpenSearch's neural search fucntionality for semantic search. Sycamore loads the vector embeddings for your dataset into a vector database in OpenSearch, and then uses vector search techniques to retreive the top results. This is used in combination with keyword search for "hybrid search," which can give better search relevance.

Most recent advances in information retrieval use semantic search. Specifically, a method called “dense retrieval”, where a neural network is used to encode passages into high-dimensional vectors. Later, at query-time, the query is also encoded into a vector in the same vector space. The best documents, then, are the ones whose vectors line up best with the query vector. 

To use dense retrieval with any kind of efficiency, you need a vector database. Vector databases are databases optimized for dense retrieval - they’re very good at finding the *n* vectors that are closest to any given query vector. 

We use OpenSearch's vector database, whch is in the [k-NN plugin](https://opensearch.org/docs/latest/search-plugins/knn/index/). With Aryn's stack, you will need to create and configure this index and neural search.

To configure an index to use k-NN, first make sure that you have the plugin installed. Then create your index with a mapping for your vector field following the k-NN docs, and use Sycamore to create and load your documents (with their encodings)

```javascript
{
  "settings": {
    "index.knn": "true",
  },
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "text": {"type": "text"},
      "embedding": {
        "type": "knn_vector",
        "dimension": int,
        "method": {
            "name": "string",
            "space_type": "string",
            "engine": "string",
            "parameters": "json_object"
        }
      }
    }
  }
}
```

That gives us the vector lookup, but we still need the query-vector generation. This comes in two steps. First, we need to load the embedding model onto the cluster so that we can access it at query-time. To do that, we can use the ml-commons plugin.

Upload embedding model

```javascript
POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
  "version": "1.0.1",
  "model_format": "TORCH_SCRIPT"
}
```

Get model id and deploy it

```javascript
GET /_plugins/_ml/tasks/<task_id>
POST /_plugins/_ml/models/<model_id>/_deploy
```

Next, we need to make use of the [neural-search plugin](https://opensearch.org/docs/latest/search-plugins/neural-search/) to tie all these components together. Neural search introduces a new kind of query `“neural”`, which encodes the query text using ml-commons, translates the query into a k-NN query, and then passes it off to k-NN for the vector database lookup.

```javascript
POST <index-name>/_search
{
  "query": {
    "neural": {
      "embedding": {
        "query_text": "Where can I find fish tacos?"
        "model_id": "<model_id>",
        "k": 100
      }
    }
  },
  "size": 10
}
```
