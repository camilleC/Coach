from typing import List

from sentence_transformers import SentenceTransformer

from ..config.settings import settings
from ..exceptions.rag_exceptions import RAGEmbeddingError
from ..utils.metrics import embedding_cache_hits


class EmbeddingClient:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as exc:
            raise RAGEmbeddingError("Failed to load embedding model", {"model": self.model_name}) from exc
        self._cache: dict[str, List[float]] = {}

    def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            outputs: List[List[float]] = []
            to_compute: List[str] = []
            for text in texts:
                if text in self._cache:
                    embedding_cache_hits.inc()
                    outputs.append(self._cache[text])
                else:
                    to_compute.append(text)
            if to_compute:
                computed = self.model.encode(to_compute, convert_to_numpy=False, normalize_embeddings=True)
                idx = 0
                for text in texts:
                    if text in self._cache:
                        continue
                    vec = computed[idx]
                    idx += 1
                    self._cache[text] = vec.tolist() if hasattr(vec, 'tolist') else list(vec)
            for text in texts:
                outputs.append(self._cache[text])
            return outputs
        except Exception as exc:
            raise RAGEmbeddingError("Failed to compute embeddings") from exc

