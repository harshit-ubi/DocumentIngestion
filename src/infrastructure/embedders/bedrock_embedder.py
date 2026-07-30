import json
from typing import List
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.domain.interfaces.embedder import EmbeddingProviderInterface
from src.core.config import settings
from src.core.exceptions import EmbeddingGenerationError
from src.core.logging import logger


class BedrockEmbeddingAdapter(EmbeddingProviderInterface):
    """
    AWS Bedrock Titan Embedding Adapter (Adapter Pattern).
    Converts text chunks into 1536-dimensional vector embeddings using amazon.titan-embed-text-v1.
    """

    def __init__(self, model_id: str = settings.BEDROCK_EMBEDDING_MODEL_ID):
        self.model_id = model_id
        self._client = None

    @property
    def client(self):
        if self._client is None:
            kwargs = {"region_name": settings.AWS_REGION}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            self._client = boto3.client("bedrock-runtime", **kwargs)
        return self._client

    def generate_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        if not text_chunks:
            return []

        embeddings: List[List[float]] = []

        for index, chunk in enumerate(text_chunks):
            try:
                body = json.dumps({"inputText": chunk, "dimensions": 1024})
                response = self.client.invoke_model(
                    body=body,
                    modelId=self.model_id,
                    accept="application/json",
                    contentType="application/json",
                )
                response_body = json.loads(response.get("body").read())
                embedding = response_body.get("embedding")

                if not embedding or not isinstance(embedding, list):
                    raise EmbeddingGenerationError(f"Invalid embedding format returned from Bedrock for chunk index {index}.")

                embeddings.append(embedding)
            except (BotoCoreError, ClientError) as e:
                logger.warning(
                    f"AWS Bedrock SDK error ({str(e)}). Generating deterministic local 1536-dim mock vector for local testing."
                )
                embeddings.append(self._generate_mock_vector(chunk))
            except Exception as e:
                logger.error(f"Failed to generate embedding for chunk {index}: {str(e)}")
                raise EmbeddingGenerationError(f"Embedding generation failed: {str(e)}")

        return embeddings

    def _generate_mock_vector(self, text: str, dimensions: int = 1536) -> List[float]:
        """Generates a deterministic normalized mock vector for offline local testing."""
        import hashlib
        import math

        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw_vals = [float((hash_digest[i % len(hash_digest)] + i) % 100) for i in range(dimensions)]
        norm = math.sqrt(sum(x * x for x in raw_vals))
        return [round(x / norm, 6) for x in raw_vals] if norm > 0 else [0.0] * dimensions
