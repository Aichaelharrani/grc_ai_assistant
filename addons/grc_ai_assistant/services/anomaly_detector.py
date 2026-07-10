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
        _logger.info("GRC AI Assistant: règle brute_force (stub).")

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
