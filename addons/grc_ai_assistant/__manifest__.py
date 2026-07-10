# -*- coding: utf-8 -*-
# Part of TRUSTIZI - Stage INT/2026/0033
{
    'name': "GRC AI Assistant",
    'summary': "Assistant IA de Gouvernance, Risques et Conformité (GRC) 100% local",
    'description': """
GRC AI Assistant
================
Module Odoo 19 permettant :
- La collecte et normalisation des journaux d'événements (ir.logging)
- La détection heuristique d'anomalies de sécurité (brute force, accès hors
  horaires, export/suppression massive, élévation de privilèges, IP inhabituelle)
- Le scoring de risque et la gestion du workflow des anomalies
- Un pipeline RAG 100% local (Ollama + Mistral 7B + nomic-embed-text + ChromaDB)
  pour répondre aux questions de conformité ISO 27001 / RGPD / Loi 09-08
- Un tableau de bord GRC et un assistant conversationnel intégré à Odoo

Développé dans le cadre du stage PFA - TRUSTIZI (INT/2026/0033).
    """,
    'author': "Aïcha EL HARRANI - TRUSTIZI",
    'website': "https://www.trustizi.com",
    'category': "Security/Compliance",
    'version': "19.0.1.0.0",
    'license': "LGPL-3",

    # Modules Odoo requis
    'depends': [
        'base',
        'mail',
        'web',
    ],

    # Dépendances Python externes (non gérées par Odoo, à documenter dans le
    # guide d'installation) : chromadb, ollama (client HTTP), langchain (optionnel)
    'external_dependencies': {
        'python': ['chromadb'],
    },

    'data': [
        # Sécurité (toujours en premier)
        'security/grc_security_groups.xml',
        'security/ir.model.access.csv',

        # Données (séquences, cron, paramètres par défaut)
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'data/ir_config_parameter_data.xml',

        # Vues
        'views/grc_log_entry_views.xml',
        'views/grc_anomaly_views.xml',
        'views/grc_policy_views.xml',
        'views/grc_ai_session_views.xml',
        'views/grc_chat_wizard_views.xml',
        'views/grc_dashboard_views.xml',
        'views/grc_menus.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'grc_ai_assistant/static/src/js/dashboard.js',
            'grc_ai_assistant/static/src/xml/dashboard.xml',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
