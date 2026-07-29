## Objective

Build a document search platform that ingests enterprise documents into configurable vector stores and exposes APIs that can be consumed by an AI agent.

The solution should demonstrate:

* API design
* Clean architecture
* Vector search
* Retrieval pipelines
* AWS integration
* Production engineering practices

---

# Part 1 – FastAPI Backend

Develop a FastAPI application exposing the following APIs.

## 1. Document Ingestion API

```
POST /documents/ingest
```

The API should:

* Accept one or more documents

  * PDF
  * DOCX
  * XLSX

* Extract text

* Chunk the document

* Generate embeddings

* Store embeddings in a vector store selected by the user.

Supported vector stores:

* Amazon OpenSearch Serverless (AOSS)
* pgvector
* Amazon S3 Vectors

Example request

```json
{
    "vector_store": "pgvector"
}
```

or

```json
{
    "vector_store": "aoss"
}
```

Persist ingestion metadata in an RDS database.

Suggested metadata:

* Document ID
* File name
* Upload timestamp
* Vector store
* Number of chunks
* Embedding model
* Status

---

## 2. Semantic Search API

```
POST /search
```

The endpoint should:

* Accept a natural language query

* Convert the query into embeddings

* Search one or more selected vector stores

Examples

Search only pgvector

```json
{
    "query": "...",
    "vector_stores": [
        "pgvector"
    ]
}
```

Search both

```json
{
    "query": "...",
    "vector_stores": [
        "pgvector",
        "aoss"
    ]
}
```

Return

* Top K chunks
* Similarity score
* Source document
* Chunk metadata

---

## 3. Embedding Migration API (Bonus)

```
POST /documents/{document_id}/transfer
```

Move all embeddings belonging to a document from one vector store to another.

Example

```json
{
    "source": "pgvector",
    "destination": "aoss"
}
```

Try to work on migration which is atomic and resumable.

---

# Part 2 – AI Agent

Develop a Strands Agent that:

* accepts a user query
* invokes the Search API as a tool
* retrieves relevant context
* generates an answer using an LLM

Deploy the agent to AWS AgentCore.

---

# Part 3 – Documentation

Include

* Architecture diagram
* Deployment steps
* Assumptions
* Design decisions
* Trade-offs
* Known limitations

---


---

# Good to have

Good to have:

* asynchronous ingestion
* background workers
* retry handling
* observability
* authentication
* Docker
* Terraform/CDK
* unit tests
* integration tests
* CI/CD

---
 