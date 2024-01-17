


## Hybrid Search

Hybrid Search is a processor that enables relevancy score normalization and combination. This allows you to make the best of both keyword and neural search, giving higher-quality results. Ordinarily this is difficult, because neural scores and keyword scores have entirely different ranges. Hybrid search enables normalization and combination of these scores in numerous varieties, so you can customize the way your search relevancy is calculated. From our testing, we've found that a `min_max` normalization with an `arithmetic_mean` (weighted `[0.111,0.889]` towards the neural score) works well, but every dataset will behave differently. To create a pipeline (called `hybrid_pipeline`) with this configuration:

```javascript
PUT /_search/pipeline/hybrid_pipeline
{
  "description": "Hybrid Search Pipeline",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [0.111, 0.889]
          }
        }
      }
    }
  ]
}
```

The hybrid search processor is called a “phase_results_processor” because it is injected in between the two phases of OpenSearch’s main search process. OpenSearch computes search results in two phases, “query”, and “fetch”. In the “query” phase, OpenSearch computes the top scores for documents and comes up with a list of the top scoring document ids. In the “fetch” phase, OpenSearch gets the source data from those document IDs and returns the list of search results that the user sees. Hybrid search interjects between the query and fetch phase, by collecting the lists of top documents and scores for each query, and normalizing and combining before the fetch phase, which keeps the computation less cumbersome. 

To use this hybrid processor, execute a hybrid query:

```javascript
GET <index-name>/_search?search_pipeline=hybrid_pipeline
{
  "query": {
    "hybrid": {
      "queries": [
        {
          "match": {
            "text_representation": "Who wrote the book of love?"
          }
        },
        {
          "neural": {
            "embedding": {
              "query_text": "Who wrote the book of love",
              "model_id": "<embedding model id>",
              "k": 100
            }
          }
        }
      ]
    }
  }
}
```


## Neural search

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
