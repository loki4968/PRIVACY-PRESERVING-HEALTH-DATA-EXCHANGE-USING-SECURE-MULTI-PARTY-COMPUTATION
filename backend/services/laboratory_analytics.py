"""
Laboratory Analytics Service
Comprehensive interpretation for CBC, CMP, and infection markers.

Implements:
- CBC interpretation with flagging and differential insights
- Comprehensive metabolic panel (CMP) assessment
- Infection/inflammation markers (CRP, ESR, Procalcitonin)
- Consolidated lab summary with recommendations
"""
from typing import Dict, List, Optional


class LaboratoryAnalytics:
    def __init__(self) -> None:
        # Adult reference ranges (typical; ranges vary by lab)
        self.ranges = {
            # CBC
            "wbc_k_ul": (4.0, 11.0),
            "rbc_m_ul": (4.2, 5.9),  # sex-dependent; using broad adult range
            "hgb_g_dl": (12.0, 17.5),
            "hct_pct": (36.0, 52.0),
            "mcv_fl": (80.0, 100.0),
            "platelets_k_ul": (150.0, 450.0),
            # CMP
            "sodium_mmol_l": (135.0, 145.0),
            "potassium_mmol_l": (3.5, 5.1),
            "chloride_mmol_l": (98.0, 107.0),
            "co2_mmol_l": (22.0, 29.0),
            "bun_mg_dl": (7.0, 20.0),
            "creatinine_mg_dl": (0.6, 1.3),
            "glucose_mg_dl": (70.0, 99.0),  # fasting
            "calcium_mg_dl": (8.6, 10.2),
            "ast_u_l": (0.0, 40.0),
            "alt_u_l": (0.0, 44.0),
            "alp_u_l": (44.0, 147.0),
            "total_bilirubin_mg_dl": (0.1, 1.2),
            "albumin_g_dl": (3.5, 5.0),
            "total_protein_g_dl": (6.0, 8.3),
            # Infection markers
            "crp_mg_l": (0.0, 5.0),
            "esr_mm_hr": (0.0, 20.0),  # age/sex dependent
            "procalcitonin_ng_ml": (0.0, 0.1),
        }

    # ----------------------------- CBC ------------------------------ #
    def analyze_cbc(self, cbc: Dict) -> Dict:
        """
        Interpret CBC values.
        Args:
            cbc: dict with keys like wbc_k_ul, rbc_m_ul, hgb_g_dl, hct_pct, mcv_fl, platelets_k_ul
        Returns:
            Dict with flags, differentials, and recommendations
        """
        result = {"flags": {}, "interpretation": [], "recommendations": []}

        def flag(key: str, label: str) -> Optional[str]:
            val = cbc.get(key)
            if val is None:
                return None
            low, high = self.ranges[key]
            if val < low:
                result["flags"][label] = "low"
                return "low"
            if val > high:
                result["flags"][label] = "high"
                return "high"
            result["flags"][label] = "normal"
            return "normal"

        # Core flags
        wbc_flag = flag("wbc_k_ul", "WBC")
        rbc_flag = flag("rbc_m_ul", "RBC")
        hgb_flag = flag("hgb_g_dl", "Hemoglobin")
        hct_flag = flag("hct_pct", "Hematocrit")
        mcv_flag = flag("mcv_fl", "MCV")
        plt_flag = flag("platelets_k_ul", "Platelets")

        # Derived anemia pattern
        if hgb_flag in ("low",) or hct_flag in ("low",):
            if mcv_flag == "low":
                result["interpretation"].append("Microcytic anemia pattern (consider iron deficiency, thalassemia)")
            elif mcv_flag == "high":
                result["interpretation"].append("Macrocytic anemia pattern (consider B12/folate deficiency, alcohol, hypothyroid)")
            else:
                result["interpretation"].append("Normocytic anemia pattern (consider chronic disease, acute blood loss)")

        # Leukocytosis/Leukopenia
        if wbc_flag == "high":
            result["interpretation"].append("Leukocytosis (infection, inflammation, stress, steroids)")
        elif wbc_flag == "low":
            result["interpretation"].append("Leukopenia (viral illness, bone marrow suppression)")

        # Thrombocytopenia/Thrombocytosis
        if plt_flag == "high":
            result["interpretation"].append("Thrombocytosis (inflammation, iron deficiency, myeloproliferative)")
        elif plt_flag == "low":
            result["interpretation"].append("Thrombocytopenia (consumption, marrow suppression, hypersplenism)")

        # Recommendations based on flags
        if hgb_flag == "low":
            result["recommendations"].extend([
                "Order iron studies (ferritin, iron, TIBC)",
                "Check B12/folate if macrocytosis",
            ])
        if wbc_flag in ("low", "high"):
            result["recommendations"].append("Correlate with differential and clinical context (infection signs)")
        if plt_flag == "low":
            result["recommendations"].append("Assess bleeding risk; review medications")

        result["values"] = {k: v for k, v in cbc.items() if v is not None}
        return result

    # ------------------------------ CMP ------------------------------ #
    def analyze_cmp(self, cmp_panel: Dict) -> Dict:
        """
        Interpret comprehensive metabolic panel.
        Keys: sodium_mmol_l, potassium_mmol_l, chloride_mmol_l, co2_mmol_l, bun_mg_dl, creatinine_mg_dl,
              glucose_mg_dl, calcium_mg_dl, ast_u_l, alt_u_l, alp_u_l, total_bilirubin_mg_dl,
              albumin_g_dl, total_protein_g_dl
        """
        result = {"flags": {}, "interpretation": [], "recommendations": []}

        def flag(key: str, label: str) -> Optional[str]:
            val = cmp_panel.get(key)
            if val is None:
                return None
            low, high = self.ranges[key]
            if val < low:
                result["flags"][label] = "low"
                return "low"
            if val > high:
                result["flags"][label] = "high"
                return "high"
            result["flags"][label] = "normal"
            return "normal"

        na_flag = flag("sodium_mmol_l", "Sodium")
        k_flag = flag("potassium_mmol_l", "Potassium")
        cr_flag = flag("creatinine_mg_dl", "Creatinine")
        glu_flag = flag("glucose_mg_dl", "Glucose (fasting)")
        ast_flag = flag("ast_u_l", "AST")
        alt_flag = flag("alt_u_l", "ALT")
        tbil_flag = flag("total_bilirubin_mg_dl", "Total Bilirubin")
        alb_flag = flag("albumin_g_dl", "Albumin")

        # Kidney function
        if cr_flag == "high" or cmp_panel.get("bun_mg_dl", 0) > self.ranges["bun_mg_dl"][1]:
            result["interpretation"].append("Possible renal impairment (elevated BUN/Creatinine)")
            result["recommendations"].append("Estimate eGFR, review nephrotoxic drugs, assess volume status")

        # Liver injury pattern
        if ast_flag == "high" or alt_flag == "high":
            result["interpretation"].append("Hepatocellular injury pattern (AST/ALT elevation)")
            result["recommendations"].append("Assess alcohol, medications, viral hepatitis serologies")
        if tbil_flag == "high":
            result["interpretation"].append("Cholestasis or impaired bilirubin handling")

        # Electrolytes
        if na_flag in ("low", "high") or k_flag in ("low", "high"):
            result["recommendations"].append("Evaluate volume status, medications, endocrine causes")

        # Glucose
        if glu_flag == "high":
            result["interpretation"].append("Hyperglycemia - screen for diabetes or stress response")
        elif glu_flag == "low":
            result["interpretation"].append("Hypoglycemia - assess medications, nutrition, endocrine")

        result["values"] = {k: v for k, v in cmp_panel.items() if v is not None}
        return result

    # ----------------------- Infection Markers ----------------------- #
    def analyze_infection_markers(self, markers: Dict) -> Dict:
        """
        Interpret CRP, ESR, Procalcitonin.
        """
        result = {"flags": {}, "interpretation": [], "recommendations": []}

        def flag(key: str, label: str) -> Optional[str]:
            val = markers.get(key)
            if val is None:
                return None
            low, high = self.ranges[key]
            if val > high:
                result["flags"][label] = "elevated"
                return "elevated"
            result["flags"][label] = "normal"
            return "normal"

        crp_flag = flag("crp_mg_l", "CRP")
        esr_flag = flag("esr_mm_hr", "ESR")
        pct_flag = flag("procalcitonin_ng_ml", "Procalcitonin")

        if crp_flag == "elevated" or esr_flag == "elevated":
            result["interpretation"].append("Inflammation present (CRP/ESR elevated)")
        if pct_flag == "elevated":
            result["interpretation"].append("Bacterial infection likely (elevated procalcitonin)")
            result["recommendations"].append("Consider antibiotics if clinically indicated; obtain cultures")

        result["values"] = {k: v for k, v in markers.items() if v is not None}
        return result

    # ----------------------- Consolidated Summary -------------------- #
    def summarize(self, cbc: Optional[Dict] = None, cmp_panel: Optional[Dict] = None, markers: Optional[Dict] = None) -> Dict:
        """
        Provide consolidated lab interpretation.
        """
        summary: Dict = {"cbc": None, "cmp": None, "infection_markers": None}
        if cbc:
            summary["cbc"] = self.analyze_cbc(cbc)
        if cmp_panel:
            summary["cmp"] = self.analyze_cmp(cmp_panel)
        if markers:
            summary["infection_markers"] = self.analyze_infection_markers(markers)
        return summary
