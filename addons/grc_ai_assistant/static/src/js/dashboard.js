/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, onWillUnmount, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const THEME_STORAGE_KEY = "grc_ai_assistant.dashboard_theme";

const ANOMALY_TYPE_LABELS = {
    brute_force: "Brute force",
    off_hours_access: "Accès hors horaires",
    mass_export: "Export massif",
    mass_deletion: "Suppression massive",
    privilege_escalation: "Élévation privilèges",
    unusual_ip: "IP inhabituelle",
};

const RISK_LEVEL_LABELS = {
    low: "Faible",
    medium: "Moyen",
    high: "Élevé",
    critical: "Critique",
};

const STATE_LABELS = {
    new: "Nouvelle",
    investigating: "En investigation",
    resolved: "Résolue",
    false_positive: "Faux positif",
};

class GrcDashboard extends Component {
    static template = "grc_ai_assistant.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.chartCanvasRef = useRef("evolutionChart");
        this.chart = null;

        this.state = useState({
            loading: true,
            theme: this._getStoredTheme(),
            totalAnomalies: 0,
            newAnomalies: 0,
            criticalAnomalies: 0,
            avgRiskScore: 0,
            byType: [],
            byState: [],
            heatmap: { rows: [], cols: [], matrix: {} },
            recent: [],
            evolution: { labels: [], data: [] },
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this._renderChart();
        });

        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }

    _getStoredTheme() {
        try {
            return localStorage.getItem(THEME_STORAGE_KEY) || "light";
        } catch {
            return "light";
        }
    }

    toggleTheme() {
        this.state.theme = this.state.theme === "dark" ? "light" : "dark";
        try {
            localStorage.setItem(THEME_STORAGE_KEY, this.state.theme);
        } catch {
            // stockage indisponible : le choix reste actif pour la session en cours
        }
        this._renderChart();
    }

    async loadDashboardData() {
        try {
            const anomalies = await this.orm.searchRead(
                "grc.anomaly",
                [],
                ["name", "anomaly_type", "risk_score", "risk_level", "state", "detection_date", "user_id"],
                { order: "detection_date desc" }
            );

            this.state.totalAnomalies = anomalies.length;
            this.state.newAnomalies = anomalies.filter((a) => a.state === "new").length;
            this.state.criticalAnomalies = anomalies.filter((a) => a.risk_level === "critical").length;

            const avg = anomalies.length
                ? anomalies.reduce((sum, a) => sum + a.risk_score, 0) / anomalies.length
                : 0;
            this.state.avgRiskScore = avg ? avg.toFixed(1) : 0;

            this.state.byType = this._countBy(anomalies, "anomaly_type", ANOMALY_TYPE_LABELS);
            this.state.byState = this._countBy(anomalies, "state", STATE_LABELS);
            this.state.heatmap = this._buildHeatmap(anomalies);
            this.state.recent = anomalies.slice(0, 8);
            this.state.evolution = this._buildEvolution(anomalies);
        } catch (error) {
            console.error("GRC Dashboard: erreur de chargement", error);
        } finally {
            this.state.loading = false;
        }
    }

    _countBy(anomalies, field, labels) {
        const counts = {};
        for (const a of anomalies) {
            const key = a[field];
            counts[key] = (counts[key] || 0) + 1;
        }
        return Object.entries(counts).map(([key, count]) => ({
            key,
            label: labels[key] || key,
            count,
        }));
    }

    _buildHeatmap(anomalies) {
        const rows = Object.keys(ANOMALY_TYPE_LABELS);
        const cols = ["low", "medium", "high", "critical"];
        const matrix = {};
        for (const row of rows) {
            matrix[row] = {};
            for (const col of cols) {
                matrix[row][col] = 0;
            }
        }
        for (const a of anomalies) {
            if (matrix[a.anomaly_type] && a.risk_level in matrix[a.anomaly_type]) {
                matrix[a.anomaly_type][a.risk_level] += 1;
            }
        }
        return {
            rows: rows.map((r) => ({ key: r, label: ANOMALY_TYPE_LABELS[r] })),
            cols: cols.map((c) => ({ key: c, label: RISK_LEVEL_LABELS[c] })),
            matrix,
        };
    }

    _buildEvolution(anomalies) {
        // Regroupe le nombre d'anomalies par jour sur les 14 derniers jours
        const days = [];
        const counts = {};
        const today = new Date();
        for (let i = 13; i >= 0; i--) {
            const d = new Date(today);
            d.setDate(d.getDate() - i);
            const key = d.toISOString().slice(0, 10);
            days.push(key);
            counts[key] = 0;
        }
        for (const a of anomalies) {
            if (!a.detection_date) continue;
            const key = a.detection_date.slice(0, 10);
            if (key in counts) {
                counts[key] += 1;
            }
        }
        return {
            labels: days.map((d) => d.slice(5)), // MM-DD
            data: days.map((d) => counts[d]),
        };
    }

    _renderChart() {
        if (!this.chartCanvasRef.el || typeof window.Chart === "undefined") {
            return;
        }
        const isDark = this.state.theme === "dark";
        const gridColor = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";
        const textColor = isDark ? "#9295AC" : "#6B7280";

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new window.Chart(this.chartCanvasRef.el.getContext("2d"), {
            type: "line",
            data: {
                labels: this.state.evolution.labels,
                datasets: [
                    {
                        label: "Anomalies détectées",
                        data: this.state.evolution.data,
                        borderColor: "#7C5CFC",
                        backgroundColor: "rgba(124,92,252,0.15)",
                        tension: 0.35,
                        fill: true,
                        pointRadius: 3,
                        pointBackgroundColor: "#7C5CFC",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: gridColor }, ticks: { color: textColor } },
                    y: {
                        beginAtZero: true,
                        ticks: { color: textColor, precision: 0 },
                        grid: { color: gridColor },
                    },
                },
            },
        });
    }

    heatCellClass(count) {
        if (!count) return "grc-heat-0";
        if (count <= 2) return "grc-heat-low";
        if (count <= 5) return "grc-heat-medium";
        return "grc-heat-high";
    }

    anomalyTypeLabel(key) {
        return ANOMALY_TYPE_LABELS[key] || key;
    }

    stateLabel(key) {
        return STATE_LABELS[key] || key;
    }

    riskLevelLabel(key) {
        return RISK_LEVEL_LABELS[key] || key;
    }

    riskBadgeClass(level) {
        return `grc-badge grc-badge-${level || "low"}`;
    }

    chipClass(field, key) {
        if (field === "state") {
            return {
                new: "grc-chip-purple",
                investigating: "grc-chip-amber",
                resolved: "grc-chip-green",
                false_positive: "grc-chip-muted",
            }[key] || "grc-chip-muted";
        }
        return "grc-chip-purple";
    }

    openAnomalies(domain = []) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Anomalies",
            res_model: "grc.anomaly",
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    openAnomaly(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "grc.anomaly",
            res_id: id,
            views: [[false, "form"]],
        });
    }
}

registry.category("actions").add("grc_ai_assistant.dashboard", GrcDashboard);

export default GrcDashboard;
