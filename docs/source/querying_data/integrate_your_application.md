# Integrating a chat UI with Aryn

The UI is a key component in many conversational search applications. A good UI enables users to search for data and see natural langauge answers and relevant search results in an easy to use interface. Additionally, UIs can show the source information for natural language answers. This tutorial will provide an overview of how you can create a simple web application that uses Aryn Conversational Search Stack's APIs for conversational search. The application will be built using React, TypeScript, and OpenAI.

## Prerequisites

This tutorial requires an already configured Aryn conversational search stack. You can follow the steps in the [Aryn E2E tutorial](https://docs.aryn.ai/tutorials/aryn-e2e-in-depth-tutorial.html) to set it up. The specific components and steps are:

1. OpenSearch 2.10+ cluster with the RAG Search Pipeline enabled
2. Hybrid Search Pipeline configured to use an OpenAI connector
3. Your data ingested into the OpenSearch cluster using Sycamore

## Building the components

### Chat sessions and conversation memory

One of the benefits of building apps with Aryn’s conversation APIs is how simple it is to manage client sessions and conversations. The API provides CRUD operations on a conversation object, which allows you to remotely store conversation state and history while not having to worry about client side memory.

Each user session can be modeled as a new `conversation` in OpenSearch. Additionally, the user can pick an existing conversation and continue from where it was left off - retaining all of the context that was used so far. A conversation’s identifier is used each time the user asks a question, so that interaction is automatically added to that conversation's history.

You access conversation memory through OpenSearch’s REST API, and it's easy to perform conversation level operations. Here is an example about how you can create a conversation in TypeScript

```typescript
const body = {
  "name": <user defined name>
}
const url = protocol + "://" + host + ":" + port + "/_plugins/_ml/memory/conversation"

try {
  const response = await fetch(url, {
      method: "POST",
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify(query),
  });
  if (!response.ok) {
      return response.text().then(text => {
          throw new Error(`Request rejected with status ${response.status} and message ${text}`);
      })
  }
  const data = await response.json();
  return data;
} catch (error: any) {
  console.error('Error sending query:', error);
  throw new Error("Error making OpenSearch query: " + error.message);
}
```

Similarly, you can list existing conversations with a GET request

```typescript
const url = protocol + "://" + host + ":" + port + "/_plugins/_ml/memory/conversation"
try {
    const response = await fetch(url, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        return response.text().then(text => {
            throw new Error(`Request rejected with status ${response.status} and message ${text}`);
        })
    }
    const data = await response.json();
    return data;
} catch (error: any) {
    console.error('Error sending query:', error);
    throw new Error("Error making OpenSearch query: " + error.message);
}
```

**********Note:********** If you have disabled OpenSearch security plugins for testing, no access control policies will be applied. This means all conversations are visible to every client accessing the cluster. In a production setup, you will want to use OpenSearch access control to restrict the conversations a user can see (see: [https://opensearch.org/docs/latest/security/access-control/index/](https://opensearch.org/docs/latest/security/access-control/index/))

### Queries and interactions

Now that we have initialized a conversation, we can move on to processing user questions and returning answers. Our application will do this through invoking the OpenSearch RAG Search Pipeline, which follows the process defined in a retrieval-augmented generation (RAG) pipeline. It follows these steps:

1. Retrieve previous interactions as conversational context
2. Retrieve relevant data in OpenSearch using hybrid search and generate search context
3. Combine the conversational context, search context, user question, and optional prompt template to create an LLM prompt
4. Make a request to LLM with the LLM prompt and get a generative response (the answer to the question)
5. Store the query, LLM prompt, and LLM response as an interaction in the conversation
6. Append the LLM response to the search results

To perform a conversational search request, see the following example

```typescript
const SOURCES = ["type", "_id", "doc_id", "properties", "title", "text_representation"]
const MODEL_ID = "<your neural search model>"
const SEARCH_PIPELINE = "rag_hybrid_pipeline"
const LLM_MODEL = "gpt4"

const userQuestion = "Who created them?"
const rephrasedQuestion = "Who created the sort benchmarks?"
const conversationId = "[active conversation id]"

const query =
{
  "_source": SOURCES,
  "query": {
      "hybrid": {
          "queries": [
              {
                  "match": {
                      "text_representation": rephrasedQuestion
                  }
              },
              {
                  "neural": {
                      "embedding": {
                          "query_text": rephrasedQuestion,
                          "k": 100,
                          "model_id": MODEL_ID
                      }
                  }
              }
          ]
      }
  },
  "ext": {
      "generative_qa_parameters": {
          "llm_question": userQuestion,
          "conversation_id": conversationId,
          "llm_model": LLM_MODEL,
      }
  },
  "size": 20
}
const url = protocol + "://" + host + ":" + port + "/" + index_name + "/_search?search_pipeline=" + SEARCH_PIPELINE

try {
  const response = await fetch(url, {
      method: "POST",
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify(query),
  });
  if (!response.ok) {
      return response.text().then(text => {
          throw new Error(`Request rejected with status ${response.status} and message ${text}`);
      })
  }

  const data = await response.json();
  return data;
} catch (error: any) {
  console.error('Error sending query:', error);
  throw new Error("Error making OpenSearch query: " + error.message);
}
```

**Document highlighting:** Certain documents, like PDFs, will contain additional metadata about what section of the documents were used to generate a response. 

For a PDF search result, the document contains a `properties` attribute, that will optionally contains `boxes`. Each box represents a page number, and the 4 coordinates of a bounding box within that page that represent the text, image, or table that was used as data. You can use a library like `react-pdf` to visualize this client side. Your component might look like this

```typescript
<Document file={url} onLoadSuccess={onDocumentLoadSuccess}>
    <Page pageNumber={pageNumber}>
        {boxes[pageNumber] && boxes[pageNumber].map((box: any, index: number) => (
            <div
                key={index}
                style={{
                    position: "absolute",
                    backgroundColor: "#ffff0033",
                    left: `${box[0] * 100}%`,
                    top: `${box[1] * 100}%`,
                    width: `${(box[2] - box[0]) * 100}%`,
                    height: `${(box[3] - box[1]) * 100}%`,
                }} />
        ))}
    </Page>
</Document>
```

### Question rewriting

A key component of conversational search is to use context during conversation to improve the way the system understands the question submitted by the user. For instance, this allows a user to ask a question like “when was it created?” because they may have previously asked “what is JouleSort?”, and the system will know “it” refers to “JouleSort” from the conversational context.

We can easily implement this in our application by passing the interactions of our `conversation` to an LLM and ask it to rephrase the question. An example can look like:

```typescript
export const generate_question_rewriting_prompt = (text: string, conversation: any()) => {
  const conversation = conversation.interactions.map((interaction) => {
      return [
        { role: "user", content: interaction.input },
        { role: "system", content: interaction.response }
      ]
  })
  const sys = "Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question. \n"
  const prompt = "Follow Up Input: " + text + "\nStandalone question: "
  const openAiPrompt = [{ role: "system", content: sys }, ...conversation, { role: "user", content: prompt }]
  return openAiPrompt;
}
const conversation = [GET conversation result]
const prompt = generate_question_rewriting_prompt("when was it created?", conversation)
// make OpenAI request with $prompt
```

## Conclusion

This tutorial showed how you can use OpenSearch’s conversational APIs contributed by Aryn to easily implement the core components of a client side conversational search application. For more details about the conversational APIs, see the official OpenSearch documentation at [https://opensearch.org/docs/latest/ml-commons-plugin/conversational-search/](https://opensearch.org/docs/latest/ml-commons-plugin/conversational-search/)