"""
LASRMIS — Main Runner
Runs the full pipeline end-to-end:
  1. Extract metrics from segmentation labels
  2. Generate reports via LLM (3 prompt strategies × 32 cases = 96 calls)
  3. Evaluate completeness, faithfulness, readability, inter-rater kappa

Usage:
    export GROQ_API_KEY=your_key_here
    python run.py

Dataset:
    Download Medical Decathlon Task05 first — see README.md.
"""

import os
import sys

from metrics    import process_all_cases
from pipeline   import run_pipeline
from evaluation import evaluate_all


def main():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        sys.exit("❌ GROQ_API_KEY not set. Export it: export GROQ_API_KEY=your_key")

    # ── Paths ────────────────────────────────────────────────────────
    label_dir   = os.path.join("data", "Task05_Prostate", "labelsTr")
    metrics_dir = os.path.join("data", "metrics")
    llm_dir     = os.path.join("data", "llm_outputs")
    eval_dir    = os.path.join("data", "evaluation")

    if not os.path.isdir(label_dir):
        sys.exit(
            f"❌ Dataset not found at {label_dir}\n"
            "   Download with:\n"
            "   wget http://medicaldecathlon.com/dataaws/Task05_Prostate.tar\n"
            "   tar -xf Task05_Prostate.tar -C data/"
        )

    # ── Stage 1: Metric extraction ────────────────────────────────────
    print("\n── Stage 1: Extracting segmentation metrics ─────────────────")
    process_all_cases(label_dir=label_dir, output_dir=metrics_dir)

    # ── Stage 2: LLM report generation ───────────────────────────────
    print("\n── Stage 2: Generating LLM reports ──────────────────────────")
    run_pipeline(
        metrics_dir=metrics_dir,
        output_dir=llm_dir,
        groq_api_key=api_key,
    )

    # ── Stage 3: Evaluation ───────────────────────────────────────────
    print("\n── Stage 3: Evaluating reports ──────────────────────────────")
    evaluate_all(llm_output_dir=llm_dir, eval_output_dir=eval_dir)

    print("\n✅ LASRMIS pipeline complete.")


if __name__ == "__main__":
    main()
