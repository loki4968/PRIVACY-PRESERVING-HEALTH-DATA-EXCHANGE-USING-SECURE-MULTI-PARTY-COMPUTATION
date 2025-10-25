"""
Vital Signs Analytics Service

Implements:
- Fever detection and temperature trend analysis
- SIRS (Systemic Inflammatory Response Syndrome) criteria evaluation
- BMI computation, categorization, and trend analysis
- Heart rate, respiratory rate, and SpO2 trend summaries
"""
from typing import Dict, List, Optional
import statistics
from datetime import datetime


class VitalSignsAnalytics:
    def __init__(self) -> None:
        # Thresholds (adult general)
        self.fever_threshold_c = 38.0
        self.hypothermia_threshold_c = 36.0
        self.tachycardia_bpm = 90
        self.tachypnea_rr = 20
        self.low_spo2_pct = 94

    # ------------------------ Temperature / Fever ------------------------ #
    def analyze_temperature(self, temp_series: List[Dict]) -> Dict:
        """
        Analyze temperature readings.
        temp_series: [{"date": "2025-09-01", "temp_c": 37.8}, ...]
        """
        if not temp_series:
            return {"error": "No temperature data provided"}

        temps = [x.get("temp_c") for x in temp_series if x.get("temp_c") is not None]
        if not temps:
            return {"error": "No valid temperature values"}

        avg = statistics.mean(temps)
        mx = max(temps)
        mn = min(temps)
        fevers = sum(1 for t in temps if t >= self.fever_threshold_c)
        hypothermia = sum(1 for t in temps if t < self.hypothermia_threshold_c)

        trend = self._trend([t for t in temps])
        status = (
            "fever" if mx >= self.fever_threshold_c else "hypothermia" if mn < self.hypothermia_threshold_c else "normal"
        )

        return {
            "average_c": round(avg, 2),
            "max_c": round(mx, 2),
            "min_c": round(mn, 2),
            "fever_readings": fevers,
            "hypothermia_readings": hypothermia,
            "trend": trend,
            "status": status,
            "recommendations": self._temp_recommendations(status),
        }

    def _temp_recommendations(self, status: str) -> List[str]:
        if status == "fever":
            return [
                "Evaluate for infection symptoms",
                "Hydration and antipyretics as needed",
                "Seek care if >39.0°C or persistent >48h",
            ]
        if status == "hypothermia":
            return [
                "Rewarm gradually and monitor",
                "Assess endocrine, environmental, or sepsis causes",
            ]
        return ["Routine monitoring"]

    # ----------------------------- SIRS ------------------------------ #
    def evaluate_sirs(self, vitals: Dict) -> Dict:
        """
        Evaluate SIRS criteria.
        Inputs (adult): temp_c, heart_rate_bpm, resp_rate_bpm, wbc_k_ul.
        SIRS positive if >=2 of:
         - Temp >38°C or <36°C
         - HR >90 bpm
         - RR >20 bpm
         - WBC >12 or <4 K/µL
        """
        temp = vitals.get("temp_c")
        hr = vitals.get("heart_rate_bpm")
        rr = vitals.get("resp_rate_bpm")
        wbc = vitals.get("wbc_k_ul")

        criteria = []
        if temp is not None and (temp > 38.0 or temp < 36.0):
            criteria.append("abnormal_temperature")
        if hr is not None and hr > self.tachycardia_bpm:
            criteria.append("tachycardia")
        if rr is not None and rr > self.tachypnea_rr:
            criteria.append("tachypnea")
        if wbc is not None and (wbc > 12.0 or wbc < 4.0):
            criteria.append("abnormal_wbc")

        sirs_positive = len(criteria) >= 2
        return {
            "criteria_met": criteria,
            "count": len(criteria),
            "sirs_positive": sirs_positive,
            "recommendations": self._sirs_recommendations(sirs_positive),
        }

    def _sirs_recommendations(self, positive: bool) -> List[str]:
        if positive:
            return [
                "Assess for sepsis: obtain cultures, consider antibiotics",
                "Monitor vitals and organ function closely",
                "Evaluate source of potential infection",
            ]
        return ["Routine monitoring; re-evaluate if clinical status changes"]

    # ------------------------------ BMI ------------------------------ #
    def bmi(self, height_cm: float, weight_kg: float) -> Dict:
        if not height_cm or not weight_kg:
            return {"error": "Height and weight are required"}
        m = height_cm / 100.0
        val = weight_kg / (m * m)
        cat = self._bmi_category(val)
        return {"bmi": round(val, 1), "category": cat}

    def bmi_trend(self, height_cm: float, weight_time_series: List[Dict]) -> Dict:
        """
        weight_time_series: [{"date": "2025-09-01", "weight_kg": 72.0}, ...]
        """
        if not weight_time_series:
            return {"error": "No weight series provided"}

        def _parse(d: str) -> datetime:
            try:
                return datetime.strptime(d, "%Y-%m-%d")
            except Exception:
                return datetime.min

        ordered = sorted(weight_time_series, key=lambda x: _parse(x.get("date", "")))
        weights = [w.get("weight_kg") for w in ordered if w.get("weight_kg") is not None]
        if not weights:
            return {"error": "No valid weights"}

        bmis = [self.bmi(height_cm, w)["bmi"] for w in weights]
        trend = self._trend(bmis)
        delta = bmis[-1] - bmis[0]
        return {
            "latest_bmi": bmis[-1],
            "baseline_bmi": bmis[0],
            "delta_bmi": round(delta, 1),
            "trend": trend,
            "category_latest": self._bmi_category(bmis[-1]),
        }

    def _bmi_category(self, bmi: float) -> str:
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25.0:
            return "Normal"
        if bmi < 30.0:
            return "Overweight"
        return "Obese"

    # ------------------------- Vitals Summary ------------------------ #
    def summarize_vitals(self, vitals_series: List[Dict]) -> Dict:
        """
        Summarize HR, RR, SpO2.
        vitals_series: [{"date": "2025-09-01", "hr": 86, "rr": 18, "spo2": 97}, ...]
        """
        if not vitals_series:
            return {"error": "No vitals data provided"}

        hr_vals = [v.get("hr") for v in vitals_series if v.get("hr") is not None]
        rr_vals = [v.get("rr") for v in vitals_series if v.get("rr") is not None]
        sp_vals = [v.get("spo2") for v in vitals_series if v.get("spo2") is not None]

        summary: Dict = {"heart_rate": {}, "resp_rate": {}, "spo2": {}}
        if hr_vals:
            summary["heart_rate"] = self._series_stats(hr_vals, threshold_high=self.tachycardia_bpm)
        if rr_vals:
            summary["resp_rate"] = self._series_stats(rr_vals, threshold_high=self.tachypnea_rr)
        if sp_vals:
            summary["spo2"] = self._series_stats(sp_vals, threshold_low=self.low_spo2_pct, higher_is_better=True)

        return summary

    def _series_stats(self, values: List[float], threshold_high: Optional[float] = None, threshold_low: Optional[float] = None, higher_is_better: bool = False) -> Dict:
        avg = statistics.mean(values)
        mx = max(values)
        mn = min(values)
        trend = self._trend(values)
        flags: List[str] = []
        if threshold_high is not None and mx > threshold_high:
            flags.append("high_values_present")
        if threshold_low is not None and mn < threshold_low:
            flags.append("low_values_present")
        status = "good" if not flags else ("caution" if higher_is_better and "low_values_present" in flags else "attention")
        return {
            "average": round(avg, 1),
            "max": mx,
            "min": mn,
            "trend": trend,
            "flags": flags,
            "status": status,
        }

    # ---------------------------- Utilities -------------------------- #
    def _trend(self, values: List[float]) -> str:
        if len(values) < 2:
            return "stable"
        return "up" if values[-1] > values[-2] else ("down" if values[-1] < values[-2] else "stable")
