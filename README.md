LASRMIS: LLM-Assisted Structured Reporting from Medical Image Segmentation
<div align="center">
https://img.shields.io/badge/python-3.8+-blue.svg
https://img.shields.io/badge/Groq-API-orange
https://img.shields.io/badge/License-MIT-yellow.svg
https://colab.research.google.com/assets/colab-badge.svg
https://img.shields.io/badge/Paper-IEEE%2520%257C%2520Springer-red
https://img.shields.io/badge/Code-GitHub-black

<h3>Bridging the gap between quantitative segmentation and clinical narrative</h3> <img src="figure_2.png" alt="LASRMIS Architecture" width="800"/> <p><i>Figure 1: LASRMIS system architecture — from segmentation masks to structured clinical reports via prompt-engineered LLMs</i></p></div>
📋 Overview
LASRMIS (LLM-Assisted Structured Reporting from Medical Image Segmentation) is a framework that automatically converts quantitative medical image segmentation outputs into structured, radiology-style clinical reports using large language models.

Medical segmentation models produce highly accurate numerical results, but translating these into clinically interpretable narratives remains a significant challenge. LASRMIS addresses this gap by:

📊 Extracting quantitative features (volume, zone, PI-RADS indicators) from segmentation masks

🧠 Processing features through prompt-engineered LLMs (Llama 3.1 via Groq)

📝 Generating structured clinical reports with radiology-style language

🔬 Evaluating outputs across clinical completeness and readability metrics

🏥 Clinical Motivation
"The clinical utility of medical image segmentation is increasingly limited not by model accuracy, but by the inability to communicate quantitative outputs in human-readable form."

Radiologists face growing workloads, and while AI segmentation models excel at quantification, their outputs require expert interpretation. LASRMIS acts as an explainability layer, making segmentation results accessible to clinicians, trainees, and patients.

🔬 Key Contributions
Prompt Ablation Study: Systematic comparison of three prompting strategies

Minimal (A): Raw metrics only

Structured (B): Clinical format with case context

Full-Context (C): Radiologist-style with uncertainty flags

Comprehensive Evaluation Framework

10-element clinical completeness scoring

Readability analysis (Flesch scores)

Reproducible methodology

Open-Source Pipeline

End-to-end from segmentation to report

Modular design for easy adaptation

📊 Key Results
Prompt Strategy	Completeness (%)	Flesch Score	Words
Minimal (A)	35.6 ± 10.9	39.5 ± 6.1	240.8
Structured (B)	76.9 ± 8.1	24.5 ± 7.3	191.7
Full-Context (C)	87.8 ± 5.4	22.2 ± 5.9	207.6
✅ Full-Context prompting achieves highest clinical completeness while maintaining appropriate domain-specific language complexity

<img src="table_1_results.png" alt="Evaluation Results" width="600"/>
🧪 Dataset
We use the Medical Segmentation Decathlon Task05 Prostate dataset:

33 multi-modal cases (T2-weighted + ADC)

Manual segmentation annotations

Peripheral zone and transition zone labels

Publicly available under CC BY-SA 4.0

<img src="figure_1.png" alt="Dataset Samples" width="600"/> <p><i>Figure 2: Sample MRI slices with segmentation overlays</i></p>
