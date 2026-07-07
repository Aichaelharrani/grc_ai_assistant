# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GrcAnomaly(models.Model):
    """Anomalie de sécurité détectée par le moteur heuristique (EF-02),
    avec scoring de risque et workflow de traitement (EF-03)."""
    _name = 'grc.anomaly'
    _description = "Anomalie de sécurité GRC"
    _order = 'risk_score desc, detection_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Référence", required=True, copy=False,
                        default=lambda self: self.env['ir.sequence'].next_by_code('grc.anomaly') or "New")

    log_entry_id = fields.Many2one(
        'grc.log.entry', string="Journal source", required=True, ondelete='cascade')
    user_id = fields.Many2one(related='log_entry_id.user_id', string="Utilisateur", store=True)

    anomaly_type = fields.Selection(
        selection=[
            ('brute_force', "Brute force"),
            ('off_hours_access', "Accès hors horaires"),
            ('mass_export', "Export massif"),
            ('mass_deletion', "Suppression massive"),
            ('privilege_escalation', "Élévation de privilèges"),
            ('unusual_ip', "IP inhabituelle"),
        ],
        string="Type d'anomalie", required=True, index=True)

    detection_date = fields.Datetime(string="Date de détection", default=fields.Datetime.now)

    # --- Scoring (EF-03) ---
    risk_score = fields.Float(string="Score de risque (0-10)", required=True)
    risk_level = fields.Selection(
        selection=[
            ('low', "Faible"),
            ('medium', "Moyen"),
            ('high', "Élevé"),
            ('critical', "Critique"),
        ],
        string="Niveau de risque", compute='_compute_risk_level', store=True)

    iso27001_control_id = fields.Char(
        string="Contrôle ISO 27001", help="Ex: A.8.16 - Surveillance des activités")

    # --- Workflow (EF-03) ---
    state = fields.Selection(
        selection=[
            ('new', "Nouvelle"),
            ('investigating', "En investigation"),
            ('resolved', "Résolue"),
            ('false_positive', "Faux positif"),
        ],
        string="État", default='new', tracking=True)

    recommendation = fields.Text(string="Recommandation IA")

    @api.depends('risk_score')
    def _compute_risk_level(self):
        for rec in self:
            if rec.risk_score >= 8:
                rec.risk_level = 'critical'
            elif rec.risk_score >= 6:
                rec.risk_level = 'high'
            elif rec.risk_score >= 4:
                rec.risk_level = 'medium'
            else:
                rec.risk_level = 'low'

    def action_send_alert_email(self):
        """Envoi de l'alerte e-mail si score >= 8 (P2)."""
        # template = self.env.ref('grc_ai_assistant.mail_template_grc_alert')
        # self.message_post_with_template(template.id)
        pass
