import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from researcher_system.analysis.dataset_analyzer import extract_datasets_from_text, analyze_dataset_usage

text = "Datasets. In consideration of the efficacy of the long-term physiological rPPG cues [8], [19], we select nine datasets (i.e., SiW [18], 3DMAD [76], HKBU-MarsV2 (HKBU) [8], MSU-MFSD (MSU) [77], 3DMask [78] and ROSE-Youtu (ROSE) [79] for FAS while FaceForensics++ (FF++) [55], DFDC [80] and CelebDFv2 [81] for face forgery detection) containing long videos (mostly >5 seconds) for the joint face spoofing and forgery detection benchmark"

found = extract_datasets_from_text(text)
print("Found Datasets:", found)

analysis = analyze_dataset_usage(found)
print("Analysis:")
import json
print(json.dumps(analysis, indent=2))
