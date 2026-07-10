# -*- coding: utf-8 -*-
from odoo import fields, models


class GrcChatWizard(models.TransientModel):
    """Wizard de conversation avec l'assistant IA GRC (EF-05).
    Sert d'interface entre la vue de chat et le pipeline RAG
    (services/rag_pipeline.py)."""
    _name = 'grc.chat.wizard'
    _description = "Assistant IA GRC - Wizard de conversation"

    question = fields.Text(string="Question")
    answer = fields.Text(string="Réponse", readonly=True)
    source_ids = fields.One2many(
        'grc.chat.wizard.source', 'wizard_id', string="Sources citées", readonly=True)

    def action_ask(self):
        """Appelée par le bouton 'Envoyer'. Interroge le pipeline RAG et
        affiche la réponse + les sources dans le même wizard."""
        self.ensure_one()
        self.source_ids.unlink()

        if not self.question or not self.question.strip():
            self.answer = "Merci de saisir une question avant d'envoyer."
            return self._reopen_self()

        result = self._ask_rag_pipeline(self.question)

        self.answer = result['answer']
        for src in result.get('sources', []):
            self.env['grc.chat.wizard.source'].create({
                'wizard_id': self.id,
                'reference': src.get('reference', ''),
                'excerpt': src.get('excerpt', ''),
                'similarity_score': src.get('similarity_score', 0.0),
            })

        # Trace de la conversation dans grc.ai.session (EF-05)
        self.env['grc.ai.session'].create({
            'question': self.question,
            'answer': result['answer'],
            'confidence_score': result.get('confidence_score', 0.0),
        })

        return self._reopen_self()

    def _ask_rag_pipeline(self, question):
        """Isole l'appel au pipeline RAG : tant que rag_pipeline.py n'est
        pas pleinement implémenté (NotImplementedError sur les méthodes
        Ollama/ChromaDB), on retourne une réponse d'attente explicite
        plutôt que de faire planter le wizard."""
        try:
            from ..services.rag_pipeline import RagPipeline
            return RagPipeline(self.env).answer_question(question)
        except NotImplementedError:
            return {
                'answer': (
                    "⚠️ Le pipeline RAG (Ollama + ChromaDB) n'est pas encore "
                    "connecté. Ceci est une réponse d'attente en attendant "
                    "l'implémentation complète de services/rag_pipeline.py."
                ),
                'sources': [],
                'confidence_score': 0.0,
            }
        except Exception as e:  # noqa: BLE001 - on veut éviter tout crash UI ici
            return {
                'answer': f"Une erreur est survenue lors de l'appel au moteur IA : {e}",
                'sources': [],
                'confidence_score': 0.0,
            }

    def _reopen_self(self):
        """Rouvre le même wizard (pour afficher la réponse sans fermer la fenêtre)."""
        return {
            'type': 'ir.actions.act_window',
            'name': "Assistant IA GRC",
            'res_model': 'grc.chat.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }


class GrcChatWizardSource(models.TransientModel):
    """Source citée affichée dans le wizard de chat (transient, liée à
    grc.chat.wizard uniquement le temps de la session)."""
    _name = 'grc.chat.wizard.source'
    _description = "Source citée - wizard de chat"

    wizard_id = fields.Many2one('grc.chat.wizard', ondelete='cascade')
    reference = fields.Char(string="Référence")
    excerpt = fields.Text(string="Extrait")
    similarity_score = fields.Float(string="Score de similarité")
