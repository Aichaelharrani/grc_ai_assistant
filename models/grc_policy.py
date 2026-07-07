# -*- coding: utf-8 -*-
from odoo import fields, models


class GrcPolicy(models.Model):
    """Document de politique (ISO 27001, RGPD, Loi 09-08, politiques internes)
    utilisé comme source pour le pipeline RAG local (EF-04)."""
    _name = 'grc.policy'
    _description = "Document de politique / conformité GRC"
    _order = 'source_type, name'

    name = fields.Char(string="Nom du document", required=True)
    source_type = fields.Selection(
        selection=[
            ('iso27001', "ISO 27001 - Annexe A"),
            ('rgpd', "RGPD"),
            ('loi_09_08', "Loi 09-08 (Maroc)"),
            ('internal', "Politique interne TRUSTIZI"),
        ],
        string="Type de source", required=True)

    file_data = fields.Binary(string="Fichier source", attachment=True)
    file_name = fields.Char(string="Nom du fichier")

    is_indexed = fields.Boolean(string="Indexé dans ChromaDB", default=False)
    indexation_date = fields.Datetime(string="Date d'indexation")
    chunk_count = fields.Integer(string="Nombre de segments (chunks)")
    chroma_collection = fields.Char(
        string="Collection ChromaDB", default="grc_policies",
        help="Nom de la collection persistante dans ChromaDB.")

    active = fields.Boolean(default=True)

    def action_reindex(self):
        """Relance l'indexation de ce document via services/rag_pipeline.py
        (découpage 500 tokens / chevauchement 50 tokens + embeddings
        nomic-embed-text via Ollama)."""
        # from ..services.rag_pipeline import RagPipeline
        # RagPipeline(self.env).index_policy(self)
        self.write({'is_indexed': True, 'indexation_date': fields.Datetime.now()})
