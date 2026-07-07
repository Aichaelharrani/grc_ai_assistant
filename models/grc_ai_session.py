# -*- coding: utf-8 -*-
from odoo import fields, models


class GrcAiSession(models.Model):
    """Historique des échanges avec l'assistant conversationnel IA
    (question, réponse, sources citées, score de confiance)."""
    _name = 'grc.ai.session'
    _description = "Session de conversation - Assistant IA GRC"
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', string="Utilisateur",
                               default=lambda self: self.env.user, required=True)
    question = fields.Text(string="Question", required=True)
    answer = fields.Text(string="Réponse générée")

    source_ids = fields.One2many(
        'grc.ai.session.source', 'session_id', string="Sources citées")

    confidence_score = fields.Float(string="Score de confiance")
    response_time = fields.Float(string="Temps de réponse (s)")

    model_used = fields.Char(string="Modèle LLM utilisé", default="mistral:7b")


class GrcAiSessionSource(models.Model):
    """Passage source (contrôle ISO, article RGPD/Loi 09-08) cité
    dans une réponse de l'assistant IA, pour affichage/traçabilité (EF-05)."""
    _name = 'grc.ai.session.source'
    _description = "Source citée par l'assistant IA"

    session_id = fields.Many2one('grc.ai.session', string="Session", ondelete='cascade')
    policy_id = fields.Many2one('grc.policy', string="Document de politique")
    reference = fields.Char(string="Référence", help="Ex: A.8.16, Article 32 RGPD")
    excerpt = fields.Text(string="Extrait")
    similarity_score = fields.Float(string="Score de similarité cosinus")
