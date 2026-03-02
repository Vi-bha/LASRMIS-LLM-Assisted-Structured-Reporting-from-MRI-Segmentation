🧠 LASRMIS
LLM-Assisted Structured Radiology Reporting from MRI Segmentation
A Training-Free Explainability Layer for Medical Imaging AI

📌 Overview
LASRMIS is a research-oriented pipeline that converts quantitative prostate MRI segmentation outputs into structured, radiology-style clinical reports using prompt-engineered Large Language Models (LLMs).

Segmentation models produce precise volumetric outputs, but their numerical results are not directly interpretable for clinical communication. LASRMIS bridges this gap by transforming structured segmentation metrics into clinically formatted narratives using LLaMA 3.1 via the Groq API.

This framework demonstrates how prompt engineering can serve as a lightweight explainability layer for medical AI systems — without retraining segmentation models.

🎯 Key Contributions
Automatic extraction of lesion volume and zonal metrics from segmentation masks

Structured LLM-based clinical report generation

Three-level prompt ablation study:

Prompt A: Minimal raw metrics

Prompt B: Structured clinical format

Prompt C: Full contextual radiologist-style instructions

Quantitative evaluation using:

Clinical completeness scoring (10 diagnostic elements)

Flesch readability analysis

System architecture visualization

Reproducible and modular pipeline

🏥 Dataset
Medical Segmentation Decathlon — Task05 Prostate

Multi-modal MRI (T2-weighted + ADC)

32 cases

NIfTI format

Manual segmentation annotations (Peripheral zone + Transition zone)

⚙️ Pipeline Architecture
text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MRI + Mask    │ → │   Feature       │ → │   Prompt        │
│   Loading       │    │   Extraction    │    │   Construction  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Report        │ ← │   LLM           │ ← │   Prompt        │
│   Generation    │    │   Inference     │    │   Templates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
        ↓
┌─────────────────┐    ┌─────────────────┐
│   Evaluation    │ → │   Results       │
│   (Completeness │    │   Visualization │
│    + Readability│    └─────────────────┘
└─────────────────┘
Detailed Steps:
Data Loading – Load MRI and segmentation masks (NIfTI format) from MSD Task05 Prostate dataset

Feature Extraction – Extract quantitative metrics:

Total prostate volume (mL)

Lesion count

Per-zone volume (Peripheral / Transition)

PI-RADS-related indicators (based on volume thresholds)

Prompt Construction – Build prompts using three strategies (Minimal, Structured, Full-Context)

LLM Inference – Generate reports via LLaMA 3.1 (70B) using Groq API (temperature=0, deterministic)

Evaluation – Score reports on:

Clinical completeness (10-element rubric)

Flesch Reading Ease / Flesch-Kincaid Grade Level

Word count analysis

Visualization – Generate architecture diagrams and result plots

🧪 Prompt Ablation Study
We systematically evaluate three prompting strategies:

🔹 Prompt A — Minimal
text
Segmentation output: Regions: 2 Total volume: 47.297 mL PI-RADS: 5
Explain this.
🔹 Prompt B — Structured
text
You are a medical AI assistant helping radiologists understand prostate MRI segmentation results.

Case ID: prostate_00
Finding: 2 significant region(s) detected
Total prostate volume: 47.297 mL
Estimated PI-RADS: 5
Significant regions:
  - R1: 8.313 mL in peripheral zone
  - R8: 38.928 mL in transition zone

Generate a structured radiology report summary covering:
1. Key finding 2. Location and volume 3. Clinical significance 4. Recommended next step
🔹 Prompt C — Full Context
text
You are a medical AI assistant supporting radiologists reviewing prostate MRI segmentation outputs.
Your role is to generate structured, readable summaries — NOT to provide clinical diagnosis.

IMPORTANT: This output is AI-generated and must be reviewed by a qualified radiologist before any clinical decision.

--- SEGMENTATION RESULTS ---
Case ID: prostate_00
Significant regions detected: 2
Total prostate volume: 47.297 mL
Highest PI-RADS estimate: 5/5

Region details:
  - R1: Volume 8.313 mL | Zone: peripheral zone | PI-RADS estimate: 5 | Highly suspicious PZ lesion
  - R8: Volume 38.928 mL | Zone: transition zone | PI-RADS estimate: 4 | Suspicious TZ lesion

Note: High PI-RADS score detected. AI confidence is higher but clinical validation is mandatory.
---

Please generate a structured report with these exact sections:
1. SUMMARY OF FINDINGS
2. LESION CHARACTERISTICS
3. CLINICAL SIGNIFICANCE
4. UNCERTAINTY FLAGS
5. RECOMMENDED NEXT STEPS

Use clear, professional radiology language. Keep each section 2-3 sentences.
📊 Evaluation Results
Method	Completeness (%)	Readability (Flesch)	Avg. Words
Minimal (A)	35.6 ± 10.9	39.5 ± 6.1	240.8
Structured (B)	76.9 ± 8.1	24.5 ± 7.3	191.7
Full-Context (C)	87.8 ± 5.4	22.2 ± 5.9	207.6
📈 Key Observations
Full-Context prompting achieves highest clinical completeness (87.8%) — a 52.2% improvement over Minimal prompting

Structured prompting (76.9%) substantially outperforms Minimal (35.6%), confirming prompt design is critical

Lower Flesch scores (22.2–24.5) for structured prompts reflect appropriate use of clinical terminology, not reduced linguistic quality

Word count remains consistent across prompt types (190–240 words), indicating comparable report length

Clinical Completeness Elements (Scored)
Lesion identification

Anatomical zone specification

PI-RADS score inclusion

Volume quantification

Biopsy recommendation

Uncertainty acknowledgment

Comparison context

Clinical significance assessment

Follow-up guidance

Disclaimer inclusion

📝 Sample Output (Prompt C - Full Context)
text
SUMMARY OF FINDINGS:
Two significant regions detected in the prostate with a total volume of 47.3 mL. 
The highest PI-RADS estimate is 5/5, indicating high suspicion for clinically significant cancer.

LESION CHARACTERISTICS:
Region R1 measures 8.3 mL and is located in the peripheral zone with PI-RADS 5. 
Region R2 measures 38.9 mL in the transition zone with PI-RADS 4.

CLINICAL SIGNIFICANCE:
The peripheral zone lesion (R1) with PI-RADS 5 is highly suspicious and warrants immediate attention.
The transition zone lesion (R2) with PI-RADS 4 also requires further evaluation.

UNCERTAINTY FLAGS:
AI-generated analysis - requires radiologist verification. High PI-RADS scores detected but 
clinical correlation with patient history and risk factors is essential.

RECOMMENDED NEXT STEPS:
Targeted biopsy of the peripheral zone lesion (R1) is strongly recommended.
Multiparametric MRI findings should be discussed in multidisciplinary tumor board.
🛠️ Tech Stack
Component	Technology
Language	Python 3.8+
Medical Imaging	NiBabel, NumPy, SciPy
ML/SciComp	scikit-learn, pandas
Visualization	matplotlib
NLP/Evaluation	textstat
LLM Inference	Groq API (LLaMA 3.1 70B)
Environment	Jupyter / Google Colab
🚀 Installation
bash
# Clone repository
git clone https://github.com/yourusername/LASRMIS.git
cd LASRMIS

# Install dependencies
pip install nibabel scipy scikit-learn pandas matplotlib textstat groq python-dotenv jupyter
🔐 API Configuration
⚠️ IMPORTANT: Never hardcode API keys

Option 1: Environment Variables (Local)
bash
# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
python
# In Python
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
Option 2: Google Colab Secrets
python
# Use Colab's built-in secrets manager
from google.colab import userdata
api_key = userdata.get('GROQ_API_KEY')
Option 3: Manual Input (Development Only)
python
import os
os.environ["GROQ_API_KEY"] = "your-key-here"  # Never commit this!
📂 Project Structure
text
LASRMIS/
│
├── 📓 Lasrmis.ipynb              # Main notebook with complete pipeline
├── 📄 README.md                   # This file
├── 📄 LICENSE                     # MIT License
├── 📄 requirements.txt            # Python dependencies
├── 📄 .gitignore                   # Files to exclude from git
│
├── 📁 src/                         # Modularized code (optional)
│   ├── feature_extractor.py
│   ├── prompt_builder.py
│   ├── report_generator.py
│   ├── evaluator.py
│   └── visualizer.py
│
├── 📁 config/                      # Configuration files
│   ├── prompts.yaml
│   └── evaluation_criteria.yaml
│
├── 📁 data/                         # Dataset (not tracked in git)
│   ├── download_data.py
│   └── README.md
│
├── 📁 results/                      # Generated outputs
│   ├── reports/
│   ├── figures/
│   └── evaluation_results.csv
│
├── 📁 examples/                     # Sample outputs
│   ├── prompt_A_sample.txt
│   ├── prompt_B_sample.txt
│   └── prompt_C_sample.txt
│
└── 📁 docs/                         # Documentation
    ├── methodology.md
    └── paper_abstract.md
🔬 Research Significance
LASRMIS makes several contributions to medical AI:

Training-Free Explainability – Demonstrates LLMs as lightweight explainability layers without retraining segmentation models

Prompt Engineering Matters – Quantifies that prompt design (87.8% completeness) is more impactful than model choice for clinical narrative quality

Reproducible Framework – Provides modular, extensible pipeline for segmentation-to-report translation

Medical NLP Benchmark – Establishes evaluation rubric (10 clinical elements) for LLM-generated radiology reports

Clinical Safety – Incorporates uncertainty flags and disclaimers (Prompt C) essential for medical applications

📚 Citation
If you use LASRMIS in your research, please cite:

bibtex
@article{lasrmis2026,
  title={LASRMIS: LLM-Assisted Structured Reporting from MRI Segmentation — A Prompt Ablation Study on Prostate MRI},
  author={Your Name},
  journal={Under Review},
  year={2026}
}
For conference paper:

bibtex
@inproceedings{lasrmis2026,
  title={LASRMIS: LLM-Assisted Structured Reporting from Medical Image Segmentation},
  author={Your Name},
  booktitle={2nd Congress on Intelligent Machines and Algorithms (CIMA 2026)},
  year={2026},
  organization={Springer LNNS}
}
⚠️ Disclaimer
IMPORTANT MEDICAL DISCLAIMER

This system:

Generates AI-assisted summaries of segmentation outputs only

Does NOT provide medical diagnosis

Does NOT replace clinical judgment

MUST be reviewed by a qualified radiologist before any clinical use

Is a research tool, not a certified medical device

The authors assume no liability for clinical decisions made using this framework.

🧠 Future Work
Statistical significance testing (paired t-test between Prompt B and C)

Integration with real PACS systems

Multi-organ segmentation support (brain, chest, liver)

Automated uncertainty quantification

Comparative evaluation with encoder-decoder report generation models

Radiologist preference study / user feedback

Fine-tuned medical LLMs vs. prompted general LLMs

👩‍💻 Author
Vibhavari Tummewar
AI/ML Researcher | Medical AI | Prompt Engineering | Explainable AI

🔬 Research Focus: LLM Applications in Healthcare, Medical Image Analysis

📧 Contact: [your.email@example.com]

🔗 LinkedIn: [your-linkedin-profile]

🐦 Twitter: [your-twitter-handle]

🤝 Contributing
Contributions are welcome! Please:

Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

See CONTRIBUTING.md for detailed guidelines.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Medical Segmentation Decathlon for the prostate MRI dataset

Groq for LLM inference API access

Meta for LLaMA 3.1 model

NIT Puducherry for research support

Soft Computing Research Society for conference collaboration

📊 Project Status
✅ Complete pipeline implemented
✅ Prompt ablation study conducted
✅ Quantitative evaluation completed
✅ Conference paper submitted to CIMA 2026
✅ Code open-sourced for reproducibility

<div align="center">
⭐ If you find this work useful, please star the repository!

Report Bug · Request Feature

</div>
