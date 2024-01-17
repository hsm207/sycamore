# Hybrid and Semantic Search

You can use an OpenSearch client version 2.12+ to query your Sycamore stack, and you can run direct hybrid searches (vector + keyword) on your data.

Hybrid search is implemented an OpenSearch search processor that enables relevancy score normalization and combination. This allows you to make the best of both keyword and semantic (neural) search, giving higher-quality results. You can use Sycamore's default hybrid search configuration, or you can customize the way your search relevancy is calculated. 

## Default settings

By default, Sycamore includes a hybrid search processor called 


## Customize your hybrid search

From our testing, we've found that a `min_max` normalization with an `arithmetic_mean` (weighted `[0.111,0.889]` towards the neural score) works well, but every dataset will behave differently. To create a pipeline (called `hybrid_pipeline`) with this configuration:

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
