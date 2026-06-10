"""
LASRMIS — LLM Pipeline
Runs all 32 cases × 3 prompt strategies = 96 LLM calls via Groq.
"""

import json
import os
import time

from groq import Groq

from prompts import build_prompt


def build_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def call_llm(client: Groq, prompt: str, retries: int = 3,
             max_tokens: int = 500) -> str:
    """Call Groq LLaMA 3.1 with retry logic."""
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  ⚠️  Attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    return "ERROR: Could not generate response after retries"


def run_pipeline(
    metrics_dir: str,
    output_dir: str,
    groq_api_key: str,
    prompt_types: list[str] | None = None,
) -> list[dict]:
    """
    Run the full LASRMIS pipeline:
      - Load per-case metric JSON files
      - Build prompts A/B/C for each case
      - Call Groq LLaMA 3.1
      - Save results

    Args:
        metrics_dir:    Directory containing *_metrics.json files.
        output_dir:     Directory to write LLM output JSONs.
        groq_api_key:   Groq API key.
        prompt_types:   Subset of ["A","B","C"] to run (default: all three).

    Returns:
        List of result dicts, one per case.
    """
    if prompt_types is None:
        prompt_types = ["A", "B", "C"]

    os.makedirs(output_dir, exist_ok=True)
    client = build_client(groq_api_key)

    metric_files = sorted(
        f for f in os.listdir(metrics_dir)
        if f.endswith("_metrics.json") and f != "all_metrics.json"
    )

    total = len(metric_files)
    n_calls = total * len(prompt_types)
    print(f"🚀 {total} cases × {len(prompt_types)} prompts = {n_calls} LLM calls\n")

    all_results = []

    for idx, fname in enumerate(metric_files, 1):
        case_id = fname.replace("_metrics.json", "")
        with open(os.path.join(metrics_dir, fname)) as f:
            metrics = json.load(f)

        print(f"[{idx:2d}/{total}] {case_id}")
        case_result = {"case_id": case_id, "responses": {}}

        for ptype in prompt_types:
            print(f"        → Prompt {ptype}...", end=" ", flush=True)
            prompt   = build_prompt(metrics, ptype)
            response = call_llm(client, prompt)
            case_result["responses"][f"prompt_{ptype}"] = {
                "prompt":   prompt,
                "response": response,
            }
            print("✅")
            time.sleep(1)  # respect rate limits

        all_results.append(case_result)
        out_path = os.path.join(output_dir, f"{case_id}_llm.json")
        with open(out_path, "w") as f:
            json.dump(case_result, f, indent=2)

    combined_path = os.path.join(output_dir, "all_llm_outputs.json")
    with open(combined_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Pipeline complete — {len(all_results)} cases, "
          f"saved to {output_dir}")
    return all_results
