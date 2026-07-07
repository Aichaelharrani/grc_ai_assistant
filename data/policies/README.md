# Documents sources - Pipeline RAG

Déposez ici les documents sources à indexer (Livrable L-04) :
- ISO 27001:2022 - Annexe A (PDF ou texte)
- Articles RGPD pertinents (art. 5, 25, 32, 33)
- Loi 09-08 (Maroc) - articles 18, 19
- Politiques internes TRUSTIZI

Ces fichiers sont chargés par `grc.policy` puis indexés par
`services/rag_pipeline.py` (découpage 500 tokens / chevauchement 50 tokens,
embeddings via Ollama `nomic-embed-text`, stockage ChromaDB persistant).
