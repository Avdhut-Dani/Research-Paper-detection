import re

def analyze_rigor(text):
    """
    Analyzes the technical rigor of the paper text.
    Detects: Ablation studies, Baselines, and Statistical validation.
    """
    results = {
        "has_ablation": False,
        "has_baselines": False,
        "has_statistical_validation": False,
        "has_reproducibility": False,
        "has_methodological_depth": False,
        "has_explicit_assumptions": False,
        "ablation_mentions": [],
        "baseline_mentions": [],
        "statistical_indicators": [],
        "repro_mentions": [],
        "math_mentions": [],
        "assumption_mentions": []
    }
    
    # 1. Detect Ablation Studies
    ablation_patterns = [
        r"(?i)ablation study",
        r"(?i)impact of (each|the|different) component",
        r"(?i)component analysis",
        r"(?i)without (the )?proposed",
        r"(?i)w/o (the )?proposed",
        r"(?i)removing (the )?layer"
    ]
    for pattern in ablation_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_ablation"] = True
            results["ablation_mentions"].extend(matches)
            
    # 2. Detect Baselines / SOTA Comparison
    baseline_patterns = [
        r"(?i)compared (with|to) (the )?baselines",
        r"(?i)state-of-the-art (methods|models)",
        r"(?i)competitive analysis",
        r"(?i)previous (work|methods)",
        r"(?i)standard competitive baseline"
    ]
    for pattern in baseline_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_baselines"] = True
            results["baseline_mentions"].extend(matches)
            
    # 3. Detect Statistical Validation
    stat_patterns = [
        r"(?i)p-value",
        r"(?i)statistically significant",
        r"(?i)standard deviation",
        r"(?i)confidence interval",
        r"(?i)t-test",
        r"(?i)anova",
        r"(?i)chi-square",
        r"(?i)wilcoxon",
        r"±\s*\d+\.\d+", # Plus-minus symbol for variance
        r"(?i)multiple seeds",
        r"(?i)random seeds"
    ]
    for pattern in stat_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_statistical_validation"] = True
            results["statistical_indicators"].extend(matches)
            
    # 4. Detect Reproducibility Indicators
    repro_patterns = [
        r"(?i)github\.com/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+",
        r"(?i)supplementary material",
        r"(?i)source code (is|will be) available",
        r"(?i)reproducibility",
        r"(?i)hyperparameters",
        r"(?i)training details",
        r"(?i)data (is|will be) shared"
    ]
    results["has_reproducibility"] = False
    results["repro_mentions"] = []
    for pattern in repro_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_reproducibility"] = True
            results["repro_mentions"].extend(matches)
            
    # 5. Detect Methodological/Mathematical Rigor
    math_patterns = [
        r"(?i)theorem",
        r"(?i)proof",
        r"(?i)proposition",
        r"(?i)mathematical model",
        r"(?i)formalized",
        r"(?i)derivation",
        r"(?i)formulation",
        r"\b[A-Z]\s*=\s*(?:\\sum|\\int|\\prod|\\lim)\b" # Basic LaTeX/Equation markers
    ]
    results["has_methodological_depth"] = False
    results["math_mentions"] = []
    for pattern in math_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_methodological_depth"] = True
            results["math_mentions"].extend(matches)
            
    # 6. Detect Explicit Assumptions
    assumption_patterns = [
        r"(?i)we assume",
        r"(?i)assuming",
        r"(?i)under the assumption",
        r"(?i)simplified setting",
        r"(?i)closed-world",
        r"(?i)constraints"
    ]
    results["has_explicit_assumptions"] = False
    results["assumption_mentions"] = []
    for pattern in assumption_patterns:
        matches = re.findall(pattern, text)
        if matches:
            results["has_explicit_assumptions"] = True
            results["assumption_mentions"].extend(matches)
            
    return results
