# -*- coding: utf-8 -*-
"""
anomaly_detector.py
--------------------
Moteur de détection heuristique avec seuils configurables (via
ir.config_parameter) pour les 6 types d'anomalies définis dans le CDC (EF-02):
brute force, accès hors horaires, export massif, suppression massive,
élévation de privilèges, IP inhabituelle.
"""

import logging

_logger = logging.getLogger(__name__)

DEFAULT_THRESHOLDS = {
    'brute_force_attempts': 5,        # échecs
    'brute_force_window_minutes': 5,
    'off_hours_start': 20,            # 20h
    'off_hours_end': 7,               # 7h
    'mass_export_records': 500,
    'mass_deletion_records': 50,
}


class AnomalyDetector:

    def __init__(self, env):
        self.env = env
        self.thresholds = self._load_thresholds()

    def _load_thresholds(self):
        """Charge les seuils depuis ir.config_parameter, avec repli sur
        DEFAULT_THRESHOLDS si non configuré (data/ir_config_parameter_data.xml)."""
        icp = self.env['ir.config_parameter'].sudo()
        thresholds = dict(DEFAULT_THRESHOLDS)
        for key in thresholds:
            value = icp.get_param(f'grc_ai_assistant.{key}')
            if value:
                thresholds[key] = type(thresholds[key])(value)
        return thresholds

    def run_detection(self, log_entries):
        """Point d'entrée principal : exécute chaque règle sur le lot de
        grc.log.entry non analysés, crée les grc.anomaly correspondantes."""
        self._detect_brute_force(log_entries)
        self._detect_off_hours_access(log_entries)
        self._detect_mass_export(log_entries)
        self._detect_mass_deletion(log_entries)
        self._detect_privilege_escalation(log_entries)
        self._detect_unusual_ip(log_entries)
        log_entries.mark_as_analyzed()

    def _detect_brute_force(self, log_entries):
        """Détecte les tentatives de brute force (EF-02) :
        N échecs de connexion ou plus (seuil configurable, défaut 5) depuis
        la même adresse IP en moins de X minutes (défaut 5).

        Convention attendue sur grc.log.entry pour qu'une entrée soit
        considérée comme un échec de connexion :
            category = 'auth'  ET  action contient 'fail' (ex: 'login_failed')
        """
        threshold = self.thresholds['brute_force_attempts']
        window_minutes = self.thresholds['brute_force_window_minutes']

        failed_logins = log_entries.filtered(
            lambda e: e.category == 'auth' and e.action and 'fail' in e.action.lower() and e.ip_address
        )
        if not failed_logins:
            _logger.info("GRC AI Assistant: brute_force - aucun échec de connexion à analyser.")
            return

        # Regroupement par adresse IP
        by_ip = {}
        for entry in failed_logins:
            by_ip.setdefault(entry.ip_address, self.env['grc.log.entry'])
            by_ip[entry.ip_address] |= entry

        for ip, entries in by_ip.items():
            entries = entries.sorted(key=lambda e: e.event_datetime)
            window = self.env['grc.log.entry']

            for entry in entries:
                window |= entry
                # Ne garder dans la fenêtre que les entrées de moins de
                # `window_minutes` par rapport à la tentative courante
                window = window.filtered(
                    lambda e: (entry.event_datetime - e.event_datetime).total_seconds()
                    <= window_minutes * 60
                )

                if len(window) >= threshold:
                    already_flagged = self.env['grc.anomaly'].search([
                        ('anomaly_type', '=', 'brute_force'),
                        ('log_entry_id', 'in', window.ids),
                    ], limit=1)
                    if already_flagged:
                        continue

                    self._create_anomaly(
                        log_entry=entry,  # dernière tentative de la rafale
                        anomaly_type='brute_force',
                        risk_score=8.5,
                        iso_control='A.8.16',
                        recommendation=(
                            f"{len(window)} échecs de connexion détectés depuis l'IP "
                            f"{ip} en moins de {window_minutes} minutes. "
                            f"Recommandation : bloquer temporairement l'IP et forcer "
                            f"une réinitialisation MFA pour le(s) compte(s) ciblé(s)."
                        ),
                    )
                    _logger.info(
                        "GRC AI Assistant: anomalie brute_force créée pour IP %s (%d tentatives).",
                        ip, len(window),
                    )
                    window = self.env['grc.log.entry']  # reset après création

    def _detect_off_hours_access(self, log_entries):
        _logger.info("GRC AI Assistant: règle off_hours_access (stub).")

    def _detect_mass_export(self, log_entries):
        _logger.info("GRC AI Assistant: règle mass_export (stub).")

    def _detect_mass_deletion(self, log_entries):
        _logger.info("GRC AI Assistant: règle mass_deletion (stub).")

    def _detect_privilege_escalation(self, log_entries):
        _logger.info("GRC AI Assistant: règle privilege_escalation (stub).")

    def _detect_unusual_ip(self, log_entries):
        _logger.info("GRC AI Assistant: règle unusual_ip (stub).")

    def _create_anomaly(self, log_entry, anomaly_type, risk_score, iso_control, recommendation=""):
        return self.env['grc.anomaly'].create({
            'log_entry_id': log_entry.id,
            'anomaly_type': anomaly_type,
            'risk_score': risk_score,
            'iso27001_control_id': iso_control,
            'recommendation': recommendation,
        })
