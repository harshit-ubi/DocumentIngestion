# 📜 API Contracts Quick Reference

Base URL: `http://localhost:8000/api/v1`

---

## 1️⃣ Ingest Document

### Request
```http
POST /api/v1/documents/ingest
Content-Type: multipart/form-data

file: [sample_document.pdf]
vector_store: "pgvector"
```

### Response (`202 Accepted`)
```json
{
  "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "PROCESSING",
  "message": "Document 'sample_document.pdf' accepted for processing in vector store 'pgvector'."
}
```

---

## 2️⃣ Check Ingestion Status

### Request
```http
GET /api/v1/documents/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### Response (`200 OK`)
```json
{
  "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "file_name": "sample_document.pdf",
  "file_type": "pdf",
  "file_size": 1048576,
  "vector_store": "pgvector",
  "embedding_model": "amazon.titan-embed-text-v1",
  "number_of_chunks": 25,
  "status": "COMPLETED",
  "error_message": null,
  "created_at": "2026-07-27T16:20:00Z",
  "updated_at": "2026-07-27T16:20:05Z"
}
```

---

## 3️⃣ List All Documents

### Request
```http
GET /api/v1/documents
```

### Response (`200 OK`)
```json
{
  "total": 1,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "file_name": "sample_document.pdf",
      "file_type": "pdf",
      "vector_store": "pgvector",
      "status": "COMPLETED",
      "number_of_chunks": 25
    }
  ]
}
```

---

## 4️⃣ Delete Document

### Request
```http
DELETE /api/v1/documents/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### Response (`200 OK`)
```json
{
  "document_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "message": "Document and all associated vector chunks deleted successfully."
}
```

---

## 5️⃣ System Health Check

### Request
```http
GET /api/v1/health
```

### Response (`200 OK`)
```json
{
  "status": "healthy",
  "service": "Document Ingestion Platform"
}
```
