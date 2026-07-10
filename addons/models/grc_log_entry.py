# -*- coding: utf-8 -*-
from odoo import api, fields, models


class GrcLogEntry(models.Model):
    """Journal d'événement normalisé, alimenté depuis ir.logging,
    les fichiers systèmes et/ou mail.message (EF-01).
    """
    _name = 'grc.log.entry'
    _description = "Journal d'événement GRC"
    _order = 'event_datetime desc'
    _rec_name = 'display_name'

    # --- Identification de l'événement ---
    event_datetime = fields.Datetime(
        string="Horodatage", required=True, index=True,
        help="Date et heure de l'événement source.")
    user_id = fields.Many2one(
        'res.users', string="Utilisateur", index=True, ondelete='set null')
    ip_address = fields.Char(string="Adresse IP", index=True)
    action = fields.Char(string="Action", required=True,
                          help="Action réalisée (ex: login, write, unlink, export).")
    odoo_model = fields.Char(string="Modèle Odoo concerné")
    odoo_res_id = fields.Integer(string="ID de l'enregistrement concerné")

    # --- Catégorisation (EF-01) ---
    category = fields.Selection(
        selection=[
            ('auth', "Authentification"),
            ('data_access', "Accès données"),
            ('config_change', "Modification configuration"),
            ('export', "Export"),
        ],
        string="Catégorie", required=True, index=True)

    # --- Traçabilité de la source ---
    source = fields.Selection(
        selection=[
            ('ir_logging', "ir.logging"),
            ('system_file', "Fichier système"),
            ('mail_message', "mail.message"),
        ],
        string="Source", required=True, default='ir_logging')
    raw_payload = fields.Text(string="Contenu brut", help="Ligne de log originale, non modifiée.")

    # --- Traitement / anti-doublon ---
    is_analyzed = fields.Boolean(
        string="Analysé", default=False, index=True,
        help="Passe à True après traitement par le moteur de détection d'anomalies.")
    analyzed_date = fields.Datetime(string="Date d'analyse")

    anomaly_ids = fields.One2many(
        'grc.anomaly', 'log_entry_id', string="Anomalies liées")

    # --- RGPD / Loi 09-08 (EF-06) ---
    ip_anonymized = fields.Boolean(string="IP anonymisée", default=False)

    display_name = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('action', 'user_id', 'event_datetime')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.action} - {rec.user_id.name or 'N/A'} ({rec.event_datetime})"

    def mark_as_analyzed(self):
        """Marque les entrées comme analysées après passage dans le moteur
        de détection (services/anomaly_detector.py)."""
        self.write({
            'is_analyzed': True,
            'analyzed_date': fields.Datetime.now(),
        })

    @api.model
    def _cron_ingest_logs(self):
        """Point d'entrée du cron d'ingestion horaire (data/ir_cron_data.xml).
        Délègue le travail réel au service log_parser.py.
        """
        # from ..services.log_parser import LogParser
        # LogParser(self.env).ingest_ir_logging()
        # LogParser(self.env).ingest_system_files()
        return True
