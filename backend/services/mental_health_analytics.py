"""
Mental Health Analytics Service
Evidence-based mental health scoring and monitoring utilities

Implements:
- PHQ-9 depression severity scoring and interpretation
- GAD-7 anxiety severity scoring and interpretation
- Suicide risk screening (based on PHQ-9 item 9 and additional flags)
- Treatment response tracking over time
"""

from typing import Dict, List, Optional
import statistics
from datetime import datetime


class MentalHealthAnalytics:
    """
    Comprehensive mental health analytics including:
    - PHQ-9 and GAD-7 scoring with clinical interpretation
    - Suicide risk screening and escalation guidance
    - Longitudinal treatment response metrics
    """

    def __init__(self) -> None:
        # PHQ-9 and GAD-7 both scored 0-3 per item
        self.phq9_thresholds = [
            (0, 4, "None-minimal"),
            (5, 9, "Mild"),
            (10, 14, "Moderate"),
            (15, 19, "Moderately Severe"),
            (20, 27, "Severe"),
        ]
        self.gad7_thresholds = [
            (0, 4, "Minimal"),
            (5, 9, "Mild"),
            (10, 14, "Moderate"),
            (15, 21, "Severe"),
        ]

    # ----------------------------- PHQ-9 ----------------------------- #
    def score_phq9(self, responses: List[int]) -> Dict:
        """
        Score PHQ-9 questionnaire.
        Args:
            responses: List of 9 integers in [0,3]
        Returns:
            Dict with total score, severity, and clinical guidance
        """
        if len(responses) != 9:
            return {"error": "PHQ-9 requires exactly 9 item responses"}
        if any((r is None or r < 0 or r > 3) for r in responses):
            return {"error": "Each PHQ-9 response must be an integer between 0 and 3"}

        total = sum(responses)
        severity = self._map_threshold(total, self.phq9_thresholds)

        # Item 9 is suicidal ideation; index 8
        item9 = responses[8]
        suicide_flag = item9 > 0

        return {
            "instrument": "PHQ-9",
            "total_score": total,
            "severity": severity,
            "item9_suicidal_ideation": bool(suicide_flag),
            "clinical_guidance": self._phq9_guidance(severity, suicide_flag),
        }

    def _phq9_guidance(self, severity: str, suicidal_ideation: bool) -> List[str]:
        guidance: List[str] = []
        if suicidal_ideation:
            guidance.extend([
                "Immediate safety assessment required (positive PHQ-9 item 9)",
                "Consider urgent referral to mental health services",
                "Assess for plan, means, and intent; create safety plan",
            ])
        if severity in ("None-minimal", "Minimal"):
            guidance.extend([
                "Provide education, watchful waiting",
                "Re-screen in 4-6 weeks if symptoms persist",
            ])
        elif severity == "Mild":
            guidance.extend([
                "Active monitoring and psychoeducation",
                "Consider brief counseling or low-intensity interventions",
            ])
        elif severity == "Moderate":
            guidance.extend([
                "Initiate psychotherapy and/or pharmacotherapy",
                "Develop follow-up plan within 4 weeks",
            ])
        elif severity == "Moderately Severe":
            guidance.extend([
                "Combine psychotherapy with pharmacotherapy",
                "Consider referral to specialist",
                "Close follow-up within 2-4 weeks",
            ])
        else:  # Severe
            guidance.extend([
                "Urgent psychiatric evaluation recommended",
                "Intensive treatment and close follow-up",
            ])
        return guidance

    # ----------------------------- GAD-7 ----------------------------- #
    def score_gad7(self, responses: List[int]) -> Dict:
        """
        Score GAD-7 questionnaire.
        Args:
            responses: List of 7 integers in [0,3]
        Returns:
            Dict with total score, severity, and guidance
        """
        if len(responses) != 7:
            return {"error": "GAD-7 requires exactly 7 item responses"}
        if any((r is None or r < 0 or r > 3) for r in responses):
            return {"error": "Each GAD-7 response must be an integer between 0 and 3"}

        total = sum(responses)
        severity = self._map_threshold(total, self.gad7_thresholds)
        return {
            "instrument": "GAD-7",
            "total_score": total,
            "severity": severity,
            "clinical_guidance": self._gad7_guidance(severity),
        }

    def _gad7_guidance(self, severity: str) -> List[str]:
        guidance: List[str] = []
        if severity in ("None-minimal", "Minimal"):
            guidance.extend(["Reassurance and watchful waiting", "Self-help resources"])
        elif severity == "Mild":
            guidance.extend(["Low-intensity CBT", "Stress management and sleep hygiene"])
        elif severity == "Moderate":
            guidance.extend(["CBT or pharmacotherapy", "Follow-up in 4 weeks"])
        else:  # Severe
            guidance.extend(["CBT plus pharmacotherapy", "Consider specialist referral"])
        return guidance

    # -------------------- Suicide Risk Screening --------------------- #
    def suicide_risk_screen(self, phq9_responses: List[int], risk_flags: Optional[Dict] = None) -> Dict:
        """
        Basic suicide risk screening leveraging PHQ-9 item 9 and contextual risk flags.
        Args:
            phq9_responses: 9-item PHQ-9 responses
            risk_flags: Optional dict of additional boolean/contextual indicators, e.g.,
                {
                    "previous_attempt": True,
                    "substance_use": True,
                    "recent_loss": False,
                    "access_to_means": False,
                }
        Returns:
            Dict with risk stratification and next-step recommendations
        """
        phq = self.score_phq9(phq9_responses)
        if "error" in phq:
            return phq

        flags = risk_flags or {}
        ideation = phq.get("item9_suicidal_ideation", False)

        # Simple additive risk model
        score = 0
        contributors: List[str] = []
        if ideation:
            score += 3
            contributors.append("PHQ-9 item 9 positive")
        for key, weight in {
            "previous_attempt": 3,
            "access_to_means": 2,
            "substance_use": 1,
            "recent_loss": 1,
            "severe_depression": 2,
        }.items():
            if key == "severe_depression":
                if phq.get("severity") in ("Moderately Severe", "Severe"):
                    score += weight
                    contributors.append("Depression severity high")
            elif flags.get(key):
                score += weight
                contributors.append(key.replace("_", " "))

        if score >= 6:
            level = "High"
        elif score >= 3:
            level = "Moderate"
        else:
            level = "Low"

        recommendations = [
            "Document assessment and safety plan",
            "Provide crisis resources and 24/7 helpline",
        ]
        if level == "High":
            recommendations = [
                "Immediate safety measures (constant observation if inpatient)",
                "Urgent psychiatric evaluation",
                "Consider hospitalization if necessary",
                "Remove access to lethal means",
                "Engage family/support system",
            ]
        elif level == "Moderate":
            recommendations.extend([
                "Expedited mental health referral",
                "Close follow-up within 48-72 hours",
            ])
        else:
            recommendations.extend(["Follow-up within 1-2 weeks", "Reassess if symptoms worsen"])

        return {
            "risk_level": level,
            "risk_score": score,
            "contributors": contributors,
            "recommendations": recommendations,
        }

    # ---------------- Treatment Response Tracking -------------------- #
    def treatment_response(self, longitudinal_scores: List[Dict[str, int]]) -> Dict:
        """
        Track treatment response over time for PHQ-9 and/or GAD-7.
        Args:
            longitudinal_scores: List of dicts like
                [{"date": "2025-09-01", "phq9": 18, "gad7": 15}, ...]
        Returns:
            Dict with deltas, percent improvements, and response category
        """
        if not longitudinal_scores:
            return {"error": "No longitudinal scores provided"}

        # Sort by date ascending
        def _parse(d: str) -> datetime:
            try:
                return datetime.strptime(d, "%Y-%m-%d")
            except Exception:
                return datetime.min

        series = sorted(longitudinal_scores, key=lambda x: _parse(x.get("date", "")))
        first = series[0]
        last = series[-1]

        def _metrics(key: str) -> Dict:
            if key not in first or key not in last:
                return {"available": False}
            delta = last[key] - first[key]
            pct = ((first[key] - last[key]) / first[key] * 100) if first[key] else 0
            values = [s.get(key) for s in series if s.get(key) is not None]
            trend = "improved" if delta < 0 else ("worsened" if delta > 0 else "stable")
            return {
                "available": True,
                "baseline": first[key],
                "latest": last[key],
                "delta": delta,
                "percent_improvement": round(pct, 1),
                "trend": trend,
                "mean": round(statistics.mean(values), 1) if values else None,
            }

        phq9_metrics = _metrics("phq9")
        gad7_metrics = _metrics("gad7")

        # Overall response category prefers PHQ-9 if available
        overall: str
        ref = phq9_metrics if phq9_metrics.get("available") else gad7_metrics
        if not ref.get("available"):
            overall = "insufficient_data"
        else:
            imp = ref.get("percent_improvement", 0)
            if imp >= 50:
                overall = "remission_or_major_response"
            elif imp >= 20:
                overall = "response"
            elif imp >= 10:
                overall = "partial_response"
            else:
                overall = "minimal_or_no_response"

        return {
            "phq9": phq9_metrics,
            "gad7": gad7_metrics,
            "overall_response": overall,
            "follow_up": self._follow_up_recommendations(overall),
        }

    # --------------------------- Utilities --------------------------- #
    def _map_threshold(self, score: int, thresholds: List[tuple]) -> str:
        for low, high, label in thresholds:
            if low <= score <= high:
                return label
        return "Unknown"

    def _follow_up_recommendations(self, category: str) -> List[str]:
        if category == "remission_or_major_response":
            return [
                "Maintain current therapy",
                "Space follow-ups to 4-8 weeks",
                "Monitor for relapse",
            ]
        if category == "response":
            return [
                "Continue therapy; consider optimization",
                "Follow-up in 2-4 weeks",
            ]
        if category == "partial_response":
            return [
                "Adjust treatment plan (optimize dose/CBT)",
                "Increase visit frequency",
            ]
        if category == "minimal_or_no_response":
            return [
                "Re-evaluate diagnosis, adherence, comorbidities",
                "Consider treatment switch or augmentation",
                "Close follow-up (1-2 weeks)",
            ]
        return ["Insufficient data; obtain baseline and follow-up scores"]
