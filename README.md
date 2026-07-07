# grc_ai_assistant

Module Odoo 19 — Assistant IA de Gouvernance, Risques & Conformité (GRC)
TRUSTIZI — Stage INT/2026/0033 — Aïcha EL HARRANI (ENSET Mohammedia)

## Structure

```
grc_ai_assistant/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── grc_log_entry.py        # EF-01 : journaux normalisés
│   ├── grc_anomaly.py          # EF-02/EF-03 : anomalies + scoring + workflow
│   ├── grc_policy.py           # EF-04 : documents source du RAG
│   └── grc_ai_session.py       # EF-05 : historique assistant conversationnel
├── services/
│   ├── __init__.py
│   ├── log_parser.py           # Ingestion ir.logging / fichiers système
│   ├── anomaly_detector.py     # Moteur heuristique (6 règles)
│   └── rag_pipeline.py         # Indexation ChromaDB + génération Ollama
├── views/
│   ├── grc_log_entry_views.xml
│   ├── grc_anomaly_views.xml
│   ├── grc_policy_views.xml
│   ├── grc_ai_session_views.xml
│   ├── grc_chat_wizard_views.xml
│   ├── grc_dashboard_views.xml
│   └── grc_menus.xml
├── security/
│   ├── grc_security_groups.xml # Groupes GRC User / GRC Manager
│   └── ir.model.access.csv
├── data/
│   ├── ir_cron_data.xml        # Cron ingestion + purge RGPD
│   ├── ir_config_parameter_data.xml
│   └── policies/                # Corpus RAG (ISO/RGPD/Loi 09-08)
└── static/
    └── description/             # icon.png, banner, etc.
```

## À faire ensuite (non inclus dans ce squelette)

1. `models/grc_chat_wizard.py` — modèle `TransientModel` `grc.chat.wizard`
   référencé par `views/grc_chat_wizard_views.xml`, qui appelle
   `rag_pipeline.answer_question()`.
2. `models/grc_log_entry.py::_cron_rgpd_purge` — anonymisation IP (30j) +
   purge (90j configurable) référencée par `data/ir_cron_data.xml`.
3. Implémentation réelle des services (actuellement stubs avec logs) :
   `log_parser`, `anomaly_detector`, `rag_pipeline`.
4. `static/description/icon.png` (128x128) et `static/description/index.html`.
5. Séquence `ir.sequence` pour `grc.anomaly` (code `grc.anomaly`).
