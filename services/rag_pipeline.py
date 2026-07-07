# -*- coding: utf-8 -*-
"""
rag_pipeline.py
----------------
Pipeline RAG 100% local (EF-04) :
Phase 1 - Indexation : découpage 500 tokens / chevauchement 50 tokens,
          embeddings via Ollama (nomic-embed-text), stockage ChromaDB persistant.
Phase 2 - Retrieval + génération : embedding de la question, top-5 passages
          par similarité cosinus, prompt augmenté, génération via Mistral 7B
          (ou Llama 3.2) servi par Ollama.

Dépendances externes (à installer hors Odoo, cf. guide d'installation) :
    pip install chromadb
Ollama doit tourner en local (http://localhost:11434) avec les modèles :
    ollama pull mistral
    ollama pull nomic-embed-text
"""

import logging

_logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
CHROMA_PERSIST_DIR = "/opt/grc_ai_assistant/chroma_data"
CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50
TOP_K_RESULTS = 5


class RagPipeline:

    def __init__(self, env):
        self.env = env
        # self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # --- Phase 1 : Indexation ---
    def index_policy(self, policy):
        """Découpe policy.file_data en chunks, génère les embeddings via
        Ollama/nomic-embed-text et les stocke dans ChromaDB."""
        chunks = self._split_into_chunks(text="", size=CHUNK_SIZE_TOKENS,
                                          overlap=CHUNK_OVERLAP_TOKENS)
        _logger.info("GRC AI Assistant: indexation policy %s (%d chunks, stub).",
                     policy.name, len(chunks))

    def _split_into_chunks(self, text, size, overlap):
        raise NotImplementedError

    def _get_embedding(self, text):
        """Appelle Ollama (nomic-embed-text) pour obtenir le vecteur d'embedding."""
        # response = requests.post(f"{OLLAMA_BASE_URL}/api/embeddings",
        #                           json={"model": "nomic-embed-text", "prompt": text})
        raise NotImplementedError

    # --- Phase 2 : Retrieval + génération ---
    def answer_question(self, question):
        """Retourne un dict {answer, sources, confidence_score} en suivant
        le flux : embedding question -> top-5 ChromaDB -> prompt augmenté
        -> génération Mistral 7B via Ollama."""
        query_embedding = self._get_embedding(question)
        passages = self._search_similar_passages(query_embedding, top_k=TOP_K_RESULTS)
        prompt = self._build_augmented_prompt(question, passages)
        answer = self._generate_response(prompt)
        return {
            'answer': answer,
            'sources': passages,
            'confidence_score': 0.0,
        }

    def _search_similar_passages(self, query_embedding, top_k):
        raise NotImplementedError

    def _build_augmented_prompt(self, question, passages):
        raise NotImplementedError

    def _generate_response(self, prompt, model="mistral:7b"):
        """Appelle Ollama /api/generate avec le modèle local (Mistral 7B)."""
        # response = requests.post(f"{OLLAMA_BASE_URL}/api/generate",
        #                           json={"model": model, "prompt": prompt, "stream": False})
        raise NotImplementedError
