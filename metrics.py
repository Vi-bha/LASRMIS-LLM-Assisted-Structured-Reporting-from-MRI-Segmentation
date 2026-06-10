"""
LASRMIS — Metric Extractor
Extracts lesion volumes, anatomical zones, and PI-RADS proxy scores
from Medical Decathlon Task05 prostate segmentation labels.
"""

import json
import os

import nibabel as nib
import numpy as np
from scipy import ndimage


def _to_serializable(obj):
    """Convert numpy types to JSON-serialisable Python types."""
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _pirads_from_zone_volume(zone_name: str, vol_ml: float) -> tuple[int, str]:
    """
    Proxy PI-RADS scoring rule based on anatomical zone and lesion volume.
    Returns (pi_rads_score, significance_text).
    """
    if zone_name == "peripheral_zone":
        if vol_ml < 0.5:
            return 3, "Equivocal — small peripheral zone lesion"
        elif vol_ml < 1.5:
            return 4, "Likely clinically significant — PZ lesion"
        else:
            return 5, "Highly suspicious PZ lesion"
    else:  # transition_zone
        if vol_ml < 1.0:
            return 2, "Likely benign — small TZ nodule"
        elif vol_ml < 2.0:
            return 3, "Equivocal TZ lesion"
        else:
            return 4, "Suspicious TZ lesion"


def extract_metrics(label_path: str, case_id: str) -> dict:
    """
    Load a NIfTI segmentation label and extract structured metrics.

    Label convention (Medical Decathlon Task05):
        1 = Peripheral Zone (PZ)
        2 = Transition Zone (TZ)

    Returns a metrics dict with zones, volumes, and PI-RADS estimates.
    """
    label_nii = nib.load(label_path)
    label = label_nii.get_fdata()

    zooms = label_nii.header.get_zooms()
    voxel_spacing = tuple(float(z) for z in zooms[:3]) if len(zooms) >= 3 \
        else (0.625, 0.625, 3.6)
    voxel_volume_mm3 = float(np.prod(voxel_spacing))

    metrics: dict = {
        "case_id":       case_id,
        "voxel_spacing": list(voxel_spacing),
        "zones":         [],
    }

    zones_data = [
        ("peripheral_zone", label == 1),
        ("transition_zone",  label == 2),
    ]

    total_vol = 0.0
    total_lesions = 0
    max_pirads = 1

    for zone_name, mask in zones_data:
        if not np.any(mask):
            continue

        labeled_array, n_components = ndimage.label(mask)

        for comp_id in range(1, n_components + 1):
            component = labeled_array == comp_id
            vol_voxels = int(np.sum(component))
            vol_ml = round(float(vol_voxels * voxel_volume_mm3 / 1000), 3)

            total_vol += vol_ml
            total_lesions += 1
            pirads, significance = _pirads_from_zone_volume(zone_name, vol_ml)
            max_pirads = max(max_pirads, pirads)

            metrics["zones"].append({
                "region_id":        f"R{total_lesions}",
                "zone":             zone_name,
                "volume_ml":        vol_ml,
                "volume_voxels":    vol_voxels,
                "pi_rads_estimate": pirads,
                "significance":     significance,
            })

    metrics["num_regions"] = total_lesions
    metrics["total_prostate_volume_ml"] = round(total_vol, 3)
    metrics["pi_rads_estimate"] = max_pirads
    metrics["finding"] = (
        f"{total_lesions} region(s) segmented"
        if total_lesions > 0 else "No significant regions detected"
    )
    metrics["clinical_significance"] = (
        metrics["zones"][0]["significance"] if metrics["zones"] else "Normal scan"
    )
    return metrics


def process_all_cases(label_dir: str, output_dir: str) -> list[dict]:
    """
    Run extract_metrics on every .nii.gz file in label_dir.
    Saves per-case JSON files and a combined all_metrics.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    label_files = sorted(
        f for f in os.listdir(label_dir)
        if f.endswith(".nii.gz") and not f.startswith("._")
    )
    print(f"Processing {len(label_files)} cases...")

    results = []
    for idx, fname in enumerate(label_files, 1):
        case_id = fname.replace(".nii.gz", "")
        print(f"  [{idx:2d}/{len(label_files)}] {case_id}...", end=" ")
        try:
            m = extract_metrics(os.path.join(label_dir, fname), case_id)
            results.append(m)
            with open(os.path.join(output_dir, f"{case_id}_metrics.json"), "w") as f:
                json.dump(m, f, indent=2, default=_to_serializable)
            print("✅")
        except Exception as e:
            print(f"❌ {e}")

    with open(os.path.join(output_dir, "all_metrics.json"), "w") as f:
        json.dump(results, f, indent=2, default=_to_serializable)

    print(f"\n✅ {len(results)} cases saved to {output_dir}")
    return results
