# -*- coding: utf-8 -*-
"""
log_parser.py
-------------
Service pur (sans dépendance ORM directe hors self.env) chargé de :
- lire les entrées ir.logging non encore importées,
- lire optionnellement les fichiers /var/log/odoo/ pour les erreurs système,
- normaliser chaque entrée en grc.log.entry (EF-01).
"""

import logging

_logger = logging.getLogger(__name__)


class LogParser:

    def __init__(self, env):
        self.env = env

    def ingest_ir_logging(self):
        """Lit ir.logging et crée les grc.log.entry correspondants."""
        # domain = [('create_date', '>', last_run_date)]
        # ir_logs = self.env['ir.logging'].search(domain)
        # for log in ir_logs:
        #     self._create_entry_from_ir_logging(log)
        _logger.info("GRC AI Assistant: ingestion ir.logging (stub).")

    def ingest_system_files(self, path="/var/log/odoo/"):
        """Lit les fichiers système pour les erreurs applicatives (optionnel)."""
        _logger.info("GRC AI Assistant: ingestion fichiers système (stub): %s", path)

    def _create_entry_from_ir_logging(self, ir_log):
        """Mappe un enregistrement ir.logging vers grc.log.entry avec
        catégorisation (Authentification / Accès données / Modification
        config / Export)."""
        raise NotImplementedError
