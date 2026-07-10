# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

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

    def action_run_detection(self):
        """Action déclenchable manuellement depuis la vue liste des journaux
        (menu Action) : lance le moteur de détection sur les entrées
        sélectionnées, ou sur toutes les entrées non analysées si aucune
        sélection n'est faite. Utile pour tester/démontrer la détection
        sans attendre le cron horaire."""
        entries = self.filtered(lambda e: not e.is_analyzed)
        if not entries:
            entries = self.search([('is_analyzed', '=', False)])
        if not entries:
            return

        from ..services.anomaly_detector import AnomalyDetector
        AnomalyDetector(self.env).run_detection(entries)
        return True

    @api.model
    def _cron_ingest_logs(self):
        """Point d'entrée du cron d'ingestion horaire (data/ir_cron_data.xml).
        Délègue le travail réel au service log_parser.py.
        """
        # from ..services.log_parser import LogParser
        # LogParser(self.env).ingest_ir_logging()
        # LogParser(self.env).ingest_system_files()
        return True

    @api.model
    def _cron_rgpd_purge(self):
        """Point d'entrée du cron quotidien RGPD / Loi 09-08 (EF-06) :
        - anonymise les IP des entrées plus vieilles que le seuil configuré
          (grc_ai_assistant.ip_anonymization_days, défaut 30 jours),
        - purge (supprime) les entrées plus vieilles que le seuil de
          rétention (grc_ai_assistant.log_retention_days, défaut 90 jours).
        """
        icp = self.env['ir.config_parameter'].sudo()
        anonymization_days = int(icp.get_param('grc_ai_assistant.ip_anonymization_days', 30))
        retention_days = int(icp.get_param('grc_ai_assistant.log_retention_days', 90))

        now = fields.Datetime.now()

        # --- Anonymisation des IP (conserve les 2 premiers octets) ---
        anonymization_threshold = now - relativedelta(days=anonymization_days)
        entries_to_anonymize = self.search([
            ('event_datetime', '<', anonymization_threshold),
            ('ip_anonymized', '=', False),
            ('ip_address', '!=', False),
        ])
        for entry in entries_to_anonymize:
            entry.write({
                'ip_address': self._anonymize_ip(entry.ip_address),
                'ip_anonymized': True,
            })

        # --- Purge des journaux au-delà de la durée de rétention ---
        purge_threshold = now - relativedelta(days=retention_days)
        entries_to_purge = self.search([('event_datetime', '<', purge_threshold)])
        entries_to_purge.unlink()

        return True

    @staticmethod
    def _anonymize_ip(ip_address):
        """Ne conserve que les 2 premiers octets d'une IPv4 (ex: 192.168.x.x).
        Retourne l'IP inchangée si le format n'est pas reconnu (ex: IPv6)."""
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.0.0"
        return ip_address
