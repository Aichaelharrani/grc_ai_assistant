/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Tableau de bord GRC — version initiale (placeholder fonctionnel).
 * Affiche des compteurs simples issus de grc.anomaly, en attendant
 * l'intégration de Chart.js prévue au CDC (§5.1).
 */
class GrcDashboard extends Component {
    static template = "grc_ai_assistant.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            totalAnomalies: 0,
            newAnomalies: 0,
            criticalAnomalies: 0,
            avgRiskScore: 0,
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            const total = await this.orm.searchCount("grc.anomaly", []);
            const nouvelles = await this.orm.searchCount("grc.anomaly", [["state", "=", "new"]]);
            const critiques = await this.orm.searchCount("grc.anomaly", [["risk_level", "=", "critical"]]);

            let avg = 0;
            if (total > 0) {
                const result = await this.orm.readGroup(
                    "grc.anomaly",
                    [],
                    ["risk_score:avg"],
                    []
                );
                avg = result.length ? result[0].risk_score : 0;
            }

            this.state.totalAnomalies = total;
            this.state.newAnomalies = nouvelles;
            this.state.criticalAnomalies = critiques;
            this.state.avgRiskScore = avg ? avg.toFixed(1) : 0;
        } catch (error) {
            console.error("GRC Dashboard: erreur de chargement", error);
        } finally {
            this.state.loading = false;
        }
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
}

registry.category("actions").add("grc_ai_assistant.dashboard", GrcDashboard);

export default GrcDashboard;
