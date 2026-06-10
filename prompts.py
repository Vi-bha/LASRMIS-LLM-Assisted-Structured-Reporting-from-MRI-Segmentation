"""
LASRMIS — Prompt Constructor
Implements the three prompt strategies evaluated in the ablation study:
  A — Minimal      (35.6% clinical completeness)
  B — Structured   (76.9% clinical completeness)
  C — Full-Context (87.8% clinical completeness)
"""


def build_prompt(metrics: dict, prompt_type: str = "C",
                 min_volume_ml: float = 0.1) -> str:
    """
    Construct an LLM prompt from extracted segmentation metrics.

    Args:
        metrics:        Output dict from metrics.extract_metrics().
        prompt_type:    "A", "B", or "C".
        min_volume_ml:  Filter noise regions below this volume threshold.

    Returns:
        Prompt string ready for LLM inference.
    """
    case_id   = metrics.get("case_id", "Unknown")
    total_vol = metrics.get("total_prostate_volume_ml", 0)
    zones     = [z for z in metrics.get("zones", [])
                 if z["volume_ml"] >= min_volume_ml]

    num_regions = len(zones)
    pirads      = max((z["pi_rads_estimate"] for z in zones), default=1)
    finding     = (
        f"{num_regions} significant region(s) detected"
        if num_regions > 0 else "No significant regions detected"
    )

    # ── PROMPT A — Minimal ───────────────────────────────────────────
    if prompt_type == "A":
        return (
            f"Segmentation output:\n"
            f"Regions: {num_regions}\n"
            f"Total volume: {total_vol} mL\n"
            f"PI-RADS: {pirads}\n\n"
            f"Explain this."
        )

    # ── PROMPT B — Structured ────────────────────────────────────────
    elif prompt_type == "B":
        zone_details = "".join(
            f"\n  - {z['region_id']}: {z['volume_ml']} mL "
            f"in {z['zone'].replace('_', ' ')}"
            for z in zones
        )
        return (
            f"You are a medical AI assistant helping radiologists understand "
            f"prostate MRI segmentation results.\n\n"
            f"Case ID: {case_id}\n"
            f"Finding: {finding}\n"
            f"Total prostate volume: {total_vol} mL\n"
            f"Estimated PI-RADS: {pirads}\n"
            f"Significant regions:{zone_details}\n\n"
            f"Generate a structured radiology report summary covering:\n"
            f"1. Key finding\n"
            f"2. Location and volume\n"
            f"3. Clinical significance\n"
            f"4. Recommended next step"
        )

    # ── PROMPT C — Full-Context ──────────────────────────────────────
    elif prompt_type == "C":
        zone_details = "".join(
            f"\n  - {z['region_id']}: Volume {z['volume_ml']} mL | "
            f"Zone: {z['zone'].replace('_', ' ')} | "
            f"PI-RADS estimate: {z['pi_rads_estimate']} | "
            f"{z['significance']}"
            for z in zones
        )
        if pirads == 3:
            uncertainty = ("Note: PI-RADS 3 is equivocal. "
                           "This AI estimate carries higher uncertainty.")
        elif pirads >= 4:
            uncertainty = ("Note: High PI-RADS score detected. "
                           "AI confidence is higher but clinical validation is mandatory.")
        else:
            uncertainty = ""

        return (
            f"You are a medical AI assistant supporting radiologists reviewing "
            f"prostate MRI segmentation outputs. Your role is to generate "
            f"structured, readable summaries — NOT to provide clinical diagnosis.\n\n"
            f"IMPORTANT: This output is AI-generated and must be reviewed by a "
            f"qualified radiologist before any clinical decision.\n\n"
            f"--- SEGMENTATION RESULTS ---\n"
            f"Case ID: {case_id}\n"
            f"Significant regions detected: {num_regions}\n"
            f"Total prostate volume: {total_vol} mL\n"
            f"Highest PI-RADS estimate: {pirads}/5\n\n"
            f"Region details:{zone_details}\n\n"
            f"{uncertainty}\n"
            f"---\n\n"
            f"Please generate a structured report with these exact sections:\n"
            f"1. SUMMARY OF FINDINGS\n"
            f"2. LESION CHARACTERISTICS\n"
            f"3. CLINICAL SIGNIFICANCE\n"
            f"4. UNCERTAINTY FLAGS\n"
            f"5. RECOMMENDED NEXT STEPS\n\n"
            f"Use clear, professional radiology language. "
            f"Keep each section 2-3 sentences."
        )

    else:
        raise ValueError(f"prompt_type must be A, B, or C — got '{prompt_type}'")
