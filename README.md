<div align="center">

```
██╗      █████╗ ███████╗██████╗ ███╗   ███╗██╗███████╗
██║     ██╔══██╗██╔════╝██╔══██╗████╗ ████║██║██╔════╝
██║     ███████║███████╗██████╔╝██╔████╔██║██║███████╗
██║     ██╔══██║╚════██║██╔══██╗██║╚██╔╝██║██║╚════██║
███████╗██║  ██║███████║██║  ██║██║ ╚═╝ ██║██║███████║
╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚══════╝
```

### **LLM-Assisted Structured Reporting from Medical Image Segmentation**
*A Prompt Ablation Study on Prostate MRI*

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LLaMA 3.1](https://img.shields.io/badge/LLM-LLaMA%203.1-0467DF?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![Groq](https://img.shields.io/badge/API-Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![Dataset](https://img.shields.io/badge/Dataset-Medical%20Decathlon-27AE60?style=for-the-badge)](http://medicaldecathlon.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-Springer%20LNCS-B31B1B?style=for-the-badge&logo=arxiv&logoColor=white)](#citation)

<br/>

> *Segmentation models produce numbers. Clinicians need narratives.*
> **LASRMIS bridges that gap — no retraining required.**

<br/>

</div>

---

## 🔬 What is LASRMIS?

LASRMIS is a **training-free pipeline** that takes the numerical output of prostate MRI segmentation — lesion volumes, anatomical zones, PI-RADS indicators — and converts them into **structured, radiology-style clinical reports** using large language model prompting.

The key research question this work answers:

> **Does prompt design affect clinical report quality — and by how much?**

The answer, measured across **96 generated reports from 32 cases**:

<br/>

<div align="center">

| Prompt Strategy | Completeness ↑ | Flesch Score | Avg. Words |
|:---|:---:|:---:|:---:|
| 🔴 Minimal &nbsp;*(Prompt A)* | 35.6 ± 10.9% | 39.5 | 240.8 |
| 🟡 Structured &nbsp;*(Prompt B)* | 76.9 ± 8.1% | 24.5 | 191.7 |
| 🟢 **Full-Context** &nbsp;*(Prompt C)* | **87.8 ± 5.4%** | **22.2** | **207.6** |

*All pairwise differences significant at p < 0.01*

</div>

<br/>

---

## 🏗️ Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Prostate MRI Input (T2W + ADC)                               │
│          │                                                      │
│          ▼                                                      │
│   Ground Truth Segmentation  ←  Medical Decathlon Task05       │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────────────────────┐                              │
│   │      Metric Extractor       │                              │
│   │  • Volume (mL)              │                              │
│   │  • Zone (PZ / TZ)           │                              │
│   │  • PI-RADS proxy score      │                              │
│   │  • Lesion count             │                              │
│   └──────────────┬──────────────┘                              │
│                  │                                              │
│                  ▼                                              │
│   ┌──────────────────────────────────────────┐                 │
│   │         Prompt Constructor               │                 │
│   │   ┌──────────┬───────────┬────────────┐ │                 │
│   │   │Prompt A  │ Prompt B  │  Prompt C  │ │                 │
│   │   │(Minimal) │(Structured│(Full-Ctx)  │ │                 │
│   │   └──────────┴───────────┴────────────┘ │                 │
│   └──────────────────────────────────────────┘                 │
│                  │                                              │
│                  ▼                                              │
│         LLaMA 3.1  ←  Groq API                                 │
│                  │                                              │
│                  ▼                                              │
│   Structured Radiology Report + Evaluation                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
LASRMIS/
│
├── 📓 Lasrmis.ipynb                  # Full pipeline — run this
│
├── 📂 data/
│   └── Task05_Prostate/              # Download separately (see below)
│       ├── imagesTr/                 # T2W + ADC volumes (.nii.gz)
│       └── labelsTr/                 # Segmentation masks (.nii.gz)
│
├── 📂 outputs/
│   ├── reports/                      # Generated reports (per case × prompt)
│   └── evaluation/                   # Completeness scores + readability CSVs
│
├── 📂 figures/
│   ├── pipeline.png                  # Architecture diagram
│   └── results_chart.png             # Ablation results chart
│
└── 📄 README.md
```

---

## ⚡ Quickstart

### 1 — Clone
```bash
git clone https://github.com/yourusername/LASRMIS.git
cd LASRMIS
```

### 2 — Install dependencies
```bash
pip install nibabel numpy matplotlib textstat groq
```

### 3 — Set your Groq API key
```bash
export GROQ_API_KEY="your_key_here"
```
> ⚠️ **Do not hardcode your API key in the notebook.** Get a free key at [console.groq.com](https://console.groq.com)

### 4 — Download the dataset
```bash
wget http://medicaldecathlon.com/dataaws/Task05_Prostate.tar
tar -xf Task05_Prostate.tar -C data/
```
Or download directly from [medicaldecathlon.com](http://medicaldecathlon.com)

### 5 — Run the pipeline
Open `Lasrmis.ipynb` in Jupyter or Google Colab and run all cells.
The pipeline automatically processes **32 cases × 3 prompts = 96 LLM calls**.

---

## 🧪 The Three Prompt Strategies

<details>
<summary><b>🔴 Prompt A — Minimal</b> &nbsp;|&nbsp; 35.6% completeness &nbsp;(click to expand)</summary>

<br/>

```
Segmentation output: Regions: 2  Total volume: 47.297 mL  PI-RADS: 5
Explain this.
```

**Result:** Generic, surface-level output. Misses lesion location, per-region detail, and clinical guidance.

</details>

<details>
<summary><b>🟡 Prompt B — Structured</b> &nbsp;|&nbsp; 76.9% completeness &nbsp;(click to expand)</summary>

<br/>

```
You are a medical AI assistant helping radiologists understand
prostate MRI segmentation results.

Case ID: prostate_00
Finding: 2 significant region(s) detected
Total prostate volume: 47.297 mL  |  Estimated PI-RADS: 5
  - R1: 8.313 mL in peripheral zone
  - R8: 38.928 mL in transition zone

Generate a structured radiology report summary covering:
1. Key finding
2. Location and volume
3. Clinical significance
4. Recommended next step
```

**Result:** Zone-specific, per-lesion differentiation. Still missing uncertainty flags and disclaimers.

</details>

<details>
<summary><b>🟢 Prompt C — Full-Context</b> &nbsp;|&nbsp; 87.8% completeness &nbsp;(click to expand)</summary>

<br/>

```
You are a medical AI assistant supporting radiologists reviewing
prostate MRI segmentation outputs. Your role is to generate
structured, readable summaries — NOT to provide clinical diagnosis.

IMPORTANT: This output is AI-generated and must be reviewed by a
qualified radiologist before any clinical decision.

--- SEGMENTATION RESULTS ---
Case ID: prostate_00
Significant regions detected: 2
Total prostate volume: 47.297 mL
Highest PI-RADS estimate: 5/5

Region details:
  - R1: Volume 8.313 mL | Zone: peripheral zone | PI-RADS: 5 | Highly suspicious
  - R8: Volume 38.928 mL | Zone: transition zone | PI-RADS: 4 | Suspicious

Note: High PI-RADS score detected. Clinical validation is mandatory.
---

Sections required:
1. SUMMARY OF FINDINGS
2. LESION CHARACTERISTICS
3. CLINICAL SIGNIFICANCE
4. UNCERTAINTY FLAGS
5. RECOMMENDED NEXT STEPS

Use clear, professional radiology language. 2-3 sentences per section.
```

**Result:** Clinically complete, uncertainty-aware, actionable output across all 10 rubric elements.

</details>

---

## 📋 Sample Output — Prompt C (prostate_00)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CASE: prostate_00  |  Generated by LASRMIS  |  Prompt C
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SUMMARY OF FINDINGS
  Two significant regions detected. Total prostate volume 47.3 mL.
  Highest PI-RADS estimate 5/5 — high suspicion for clinically
  significant cancer.

  LESION CHARACTERISTICS
  R1 │ 8.313 mL │ Peripheral zone │ PI-RADS 5 │ Highly suspicious
  R8 │ 38.928 mL │ Transition zone │ PI-RADS 4 │ Suspicious

  CLINICAL SIGNIFICANCE
  The peripheral zone lesion with PI-RADS 5 warrants immediate
  clinical attention. The transition zone lesion requires further
  evaluation given its volume.

  UNCERTAINTY FLAGS
  ⚠  AI-generated — radiologist verification mandatory
  ⚠  Correlation with patient history and risk factors essential

  RECOMMENDED NEXT STEPS
  Targeted biopsy of the peripheral zone lesion is strongly
  recommended. Discuss in multidisciplinary tumour board.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📏 Clinical Completeness Rubric

Reports are scored against a **10-element checklist** grounded in radiology reporting standards:

| # | Element | What it checks |
|:---:|:---|:---|
| 1 | Lesion identification | All significant regions correctly identified |
| 2 | Anatomical zone | PZ / TZ specified per lesion |
| 3 | PI-RADS inclusion | PI-RADS estimate present and correct |
| 4 | Volume quantification | Per-lesion volumes reported in mL |
| 5 | Biopsy recommendation | Suggested when clinically indicated |
| 6 | Uncertainty acknowledgement | AI limitations explicitly noted |
| 7 | Comparison context | Reference to prior imaging where relevant |
| 8 | Clinical significance | Findings interpreted, not just listed |
| 9 | Follow-up guidance | Specific next steps stated |
| 10 | Disclaimer inclusion | Safety disclaimer present |

Plus **Flesch Reading Ease** and **word count** for linguistic characterisation.

---

## 🔑 Key Findings

```
Prompt A → Prompt B    +41.3 points completeness gain
Prompt B → Prompt C    +10.9 points completeness gain
─────────────────────────────────────────────────────
Total A → C            +52.2 points  (35.6% → 87.8%)
```

- The **model is not the bottleneck** — prompt design is
- Lower Flesch scores in clinical prompts = appropriate medical precision, not worse writing
- Structured prompts are the most **word-efficient** (191 words avg, highest information density)
- Identified failure modes: hallucination ~8% · zone confusion ~5% · generic recommendations ~12%

---

## 📚 Citation

If you use LASRMIS in your research, please cite:

```bibtex
@inproceedings{lasrmis2025,
  title     = {LASRMIS: LLM-Assisted Structured Reporting from Medical
               Image Segmentation -- A Prompt Ablation Study on Prostate MRI},
  author    = {Your Name and Co-authors},
  booktitle = {Springer LNCS},
  year      = {2025}
}
```

---

## ⚠️ Clinical Disclaimer

> This system is a **research prototype** and is not validated for clinical use.
> All generated reports are AI-assisted outputs and **must be reviewed by a qualified
> radiologist** before informing any clinical decision. LASRMIS does not perform
> diagnosis and is not a substitute for professional medical judgement.

---

## 🙏 Acknowledgements

- [Medical Segmentation Decathlon](http://medicaldecathlon.com) — Task05 Prostate dataset
- [Groq](https://groq.com) — Fast LLaMA 3.1 inference
- [Meta AI](https://ai.meta.com/llama/) — LLaMA 3.1 open model

---

<div align="center">
<br/>

*Questions or collaborations → open an issue or reach out at* `your.email@university.edu`

<br/>

⭐ *Star this repo if you find it useful!*

</div>
