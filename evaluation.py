"""
LASRMIS — Evaluation
Scores generated reports on:
  - Clinical completeness (10-element rubric)
  - Faithfulness / hallucination detection
  - Readability (Flesch Reading Ease)
  - Inter-rater reliability (Cohen's kappa)
"""

import json
import os

import numpy as np
import pandas as pd
import textstat
from sklearn.metrics import cohen_kappa_score, accuracy_score


# ── 10-element clinical completeness rubric ──────────────────────────
REQUIRED_ELEMENTS = [
    "lesion", "volume", "zone", "PI-RADS", "biopsy",
    "follow", "significant", "uncertainty", "peripheral", "transition",
]

# Terms plausible in prostate reports but NOT derivable from
# volume/zone/count input alone — proxy for hallucination
HALLUCINATION_TERMS = [
    "irregular margins", "spiculation", "capsular contact",
    "extracapsular extension", "seminal vesicle",
    "neurovascular bundle", "diffusion restriction",
    "dynamic contrast", "enhancement pattern",
    "hypointense", "hyperintense", "t2 signal",
    "wash-out", "wash-in", "early enhancement",
    "ill-defined", "well-defined margins", "lobulated",
    "necrosis", "hemorrhage",
]

# Lenient synonyms for inter-rater simulation
RATER2_KEYWORDS: dict[str, list[str]] = {
    "lesion":       ["lesion", "region", "focus", "area", "abnormality"],
    "volume":       ["volume", "size", "mL", "milliliter", "extent"],
    "zone":         ["zone", "peripheral", "transition", "PZ", "TZ"],
    "PI-RADS":      ["PI-RADS", "PIRADS", "score", "assessment"],
    "biopsy":       ["biopsy", "targeted", "sampling", "tissue"],
    "follow":       ["follow", "surveillance", "monitoring", "repeat"],
    "significant":  ["significant", "clinically", "important", "suspicious"],
    "uncertainty":  ["uncertainty", "caution", "verify", "radiologist"],
    "peripheral":   ["peripheral", "PZ", "peripheral zone"],
    "transition":   ["transition", "TZ", "transition zone"],
}

RATER1_KEYWORDS: dict[str, list[str]] = {
    k: [k] for k in REQUIRED_ELEMENTS  # strict exact-match
}


# ── Scoring functions ─────────────────────────────────────────────────

def score_completeness(text: str) -> float:
    tl = text.lower()
    found = [kw for kw in REQUIRED_ELEMENTS if kw.lower() in tl]
    return round(len(set(found)) / len(REQUIRED_ELEMENTS) * 100, 1)


def score_readability(text: str) -> float:
    try:
        return round(textstat.flesch_reading_ease(text), 1)
    except Exception:
        return 0.0


def score_word_count(text: str) -> int:
    return len(text.split())


def score_faithfulness(text: str) -> tuple[int, list[str]]:
    """
    Returns (score, list_of_hallucinated_terms).
    Score: 3=strict, 2=mostly, 1=partial, 0=substantial hallucination.
    """
    tl = text.lower()
    found = [t for t in HALLUCINATION_TERMS if t in tl]
    score = max(0, 3 - len(found))
    return score, found


def score_with_keywords(text: str,
                        keyword_dict: dict[str, list[str]]) -> dict[str, int]:
    """Binary score per element using a keyword dictionary (for kappa)."""
    tl = text.lower()
    return {
        elem: int(any(kw.lower() in tl for kw in keywords))
        for elem, keywords in keyword_dict.items()
    }


# ── Main evaluation ───────────────────────────────────────────────────

def evaluate_all(llm_output_dir: str, eval_output_dir: str) -> pd.DataFrame:
    """
    Load all_llm_outputs.json, score every report, save CSV + kappa JSON.
    Returns a DataFrame with one row per (case, prompt_type).
    """
    os.makedirs(eval_output_dir, exist_ok=True)

    with open(os.path.join(llm_output_dir, "all_llm_outputs.json")) as f:
        all_results = json.load(f)

    rows = []
    rater1_rows, rater2_rows = [], []

    for case in all_results:
        case_id = case["case_id"]
        for ptype in ["A", "B", "C"]:
            key = f"prompt_{ptype}"
            if key not in case["responses"]:
                continue
            response = case["responses"][key]["response"]
            if response.startswith("ERROR"):
                continue

            comp              = score_completeness(response)
            read              = score_readability(response)
            wc                = score_word_count(response)
            faith, hall_terms = score_faithfulness(response)

            rows.append({
                "case_id":            case_id,
                "prompt_type":        ptype,
                "completeness":       comp,
                "readability":        read,
                "word_count":         wc,
                "faithfulness":       faith,
                "hallucinated_terms": hall_terms,
            })

            r1 = score_with_keywords(response, RATER1_KEYWORDS)
            r2 = score_with_keywords(response, RATER2_KEYWORDS)
            rater1_rows.append({"case_id": case_id, "prompt_type": ptype, **r1})
            rater2_rows.append({"case_id": case_id, "prompt_type": ptype, **r2})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(eval_output_dir, "evaluation_scores.csv"), index=False)

    # Inter-rater kappa
    r1_df = pd.DataFrame(rater1_rows)
    r2_df = pd.DataFrame(rater2_rows)
    r1_df.to_csv(os.path.join(eval_output_dir, "rater1_scores.csv"), index=False)
    r2_df.to_csv(os.path.join(eval_output_dir, "rater2_scores.csv"), index=False)

    elements = list(REQUIRED_ELEMENTS)
    r1_flat  = r1_df[elements].values.flatten()
    r2_flat  = r2_df[elements].values.flatten()
    overall_kappa = round(cohen_kappa_score(r1_flat, r2_flat), 3)
    overall_acc   = round(accuracy_score(r1_flat, r2_flat) * 100, 1)

    kappa_results = {
        "overall_kappa":    overall_kappa,
        "overall_accuracy": overall_acc,
        "n_reports":        len(r1_df),
    }
    with open(os.path.join(eval_output_dir, "interrater_kappa.json"), "w") as f:
        json.dump(kappa_results, f, indent=2)

    # Summary table
    print("\n" + "=" * 75)
    print("EVALUATION SUMMARY")
    print("=" * 75)
    print(f"{'Prompt':<10} {'Completeness':>15} {'Faithfulness':>14} "
          f"{'Readability':>13} {'Words':>8}")
    print("-" * 75)
    for ptype in ["A", "B", "C"]:
        sub = df[df["prompt_type"] == ptype]
        if sub.empty:
            continue
        label = {"A": "Minimal", "B": "Structured", "C": "Full-Context"}[ptype]
        print(
            f"Prompt {ptype} ({label:<13}) "
            f"{sub['completeness'].mean():>8.1f} ± {sub['completeness'].std():.1f}%"
            f"  {sub['faithfulness'].mean():>8.2f}/3"
            f"  {sub['readability'].mean():>8.1f}"
            f"  {sub['word_count'].mean():>6.0f}"
        )
    print(f"\nInter-rater kappa: {overall_kappa} | Accuracy: {overall_acc}%")
    print(f"Saved to {eval_output_dir}")
    return df
