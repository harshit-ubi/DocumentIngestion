# Phase 1: Data Ingestion Pipeline (Python / FastAPI)

## Overview
Phase 1 implements the **Document Ingestion Pipeline** for the Document Search Platform as specified in `poc.md`.

## Confirmed Specifications
1. **Embedding Provider**: AWS Bedrock Embeddings (`amazon.titan-embed-text-v1`).
2. **Asynchronous Execution**: `POST /documents/ingest` dispatches processing to FastAPI `BackgroundTasks` and returns `202 Accepted` immediately with a `document_id`.
3. **Status Polling**: `GET /documents/{document_id}` tracks progress (`PENDING` -> `PROCESSING` -> `COMPLETED` / `FAILED`).
4. **Multi-Format Extraction**: Raw text and layout extraction from PDF (`.pdf`), Word (`.docx`), and Excel (`.xlsx`).
5. **Pluggable Vector Store Adapters**: Vector & chunk storage via user-selected vector store:
   - `pgvector` (PostgreSQL extension)
   - `aoss` (Amazon OpenSearch Serverless)
   - `s3_vectors` (Amazon S3 Vector Store)

---

## Architecture Flowchart

```mermaid
flowchart TD
    Client([Client / Frontend / SDK]) -->|POST /documents/ingest\nMultipart File + Target VectorStore| API[FastAPI Router\n/documents/ingest]
    
    API -->|1. Save Initial Metadata\nStatus = PROCESSING| Repo[(PostgreSQL / RDS Metadata)]
    API -->|2. Dispatch FastAPI BackgroundTask| Task[Ingestion Pipeline Worker]
    API -->|Return 202 Accepted + Document ID| Client
    
    subgraph Data Ingestion Pipeline (Asynchronous Worker)
        Task -->|Step A: Extract Text| Extractors{File Type Router}
        Extractors -->|.pdf| PyPDF[PdfExtractor]
        Extractors -->|.docx| Docx[DocxExtractor]
        Extractors -->|.xlsx| Xlsx[XlsxExtractor]
        
        PyPDF -->|Raw Text + Page Metadata| Chunker[Text Chunker Engine\nRecursive Character Splitter]
        Docx -->|Raw Text + Paragraph Metadata| Chunker
        Xlsx -->|Structured Rows / Sheets Text| Chunker
        
        Chunker -->|List of Chunks| Embedder[AWS Bedrock Embedding Service\namazon.titan-embed-text-v1]
        Embedder -->|Chunks + Vector Embeddings| Router{Vector Store Adapter Router}
        
        Router -->|vector_store = 'pgvector'| PgVec[(pgvector / PostgreSQL)]
        Router -->|vector_store = 'aoss'| AOSS[(Amazon OpenSearch Serverless)]
        Router -->|vector_store = 's3_vectors'| S3Vec[(Amazon S3 Vector Store)]
    end
    
    Router -->|3. Update Ingestion Metadata\nChunk Count + Status = COMPLETED| Repo
```

---

## Workspace Folder Hierarchy

```
DocumentIngestion/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml / requirements.txt
├── README.md
├── poc.md
├── phase1.md
├── alembic/                      # Database migration scripts
└── src/
    ├── main.py                   # FastAPI Application Entrypoint
    ├── core/                     # Configuration, Logging, Exceptions
    │   ├── config.py
    │   ├── logging.py
    │   └── exceptions.py
    ├── api/                      # REST API Endpoints & Pydantic Schemas
    │   ├── v1/
    │   │   ├── router.py
    │   │   └── endpoints/
    │   │       ├── health.py
    │   │       └── ingestion.py  # POST /documenots/ingest, GET /documents/{id}
    │   └── schemas/
    │       └── ingestion.py
    ├── domain/                   # Entities & Port Interfaces (Clean Architecture)
    │   ├── models/
    │   │   ├── document.py
    │   │   └── ingestion.py
    │   └── interfaces/
    │       ├── extractor.py
    │       ├── chunker.py
    │       ├── embedder.py
    │       ├── vector_store.py   # VectorStoreAdapter Base Class
    │       └── repository.py
    ├── services/                 # Business Logic & Orchestration
    │   ├── ingestion_service.py  # Background Task Ingestion Pipeline Orchestrator
    │   └── chunking_service.py
    └── infrastructure/           # Concrete Drivers & Implementations
        ├── database/
        │   ├── connection.py
        │   ├── models.py         # ORM models
        │   └── repository.py
        ├── extractors/
        │   ├── pdf_extractor.py
        │   ├── docx_extractor.py
        │   ├── xlsx_extractor.py
        │   └── factory.py
        ├── embedders/
        │   └── bedrock_embedder.py # AWS Bedrock Titan Embedding Adapter
        └── vector_stores/
            ├── base.py
            ├── pgvector.py       # pgvector adapter
            ├── aoss.py           # Amazon OpenSearch Serverless adapter
            ├── s3_vectors.py     # AWS S3 vector store adapter
            └── factory.py
```
