"""
NASA Space Apps Challenge - Astronaut Health Risk Monitoring System
Module: predict_risk.py

Purpose:
    Clinical Inference & Daily Risk Triage Engine.
    Executes an ensemble of top-performing champion ML models across all 17 astronaut
    health risk domains to classify current-day (Day t) operational risks.

Features:
    1. Multi-Domain Single-Pass Inference: Evaluates all 17 health risks simultaneously.
    2. Calibrated Probabilities: Outputs exact confidence scores [P(Low), P(Moderate), P(High)].
    3. Composite Mission Triage Index: Computes overall astronaut alert status (GREEN, AMBER, RED).
    4. Threat Ranking: Surfaces top critical clinical threats for the astronaut-day.
    5. Flexible CLI Modes:
       - Query by Astronaut & Mission Day: python predict_risk.py --astronaut AST002 --day 95
       - Batch Scoring on CSV: python predict_risk.py --input <path.csv> --output <results.csv>
       - Quick Smoke Test / Demo Mode: python predict_risk.py --demo
"""

import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent

# Ensure project root is in path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from feature_selection import FEATURE_CONFIG
from integrate_datasets import SOURCES

MODELS_DIR = PROJECT_ROOT / "trained_models"
INTEGRATED_DATASET_PATH = PROJECT_ROOT / "datasets" / "integrated" / "astronaut_health_integrated.csv"

# Pre-selected champion algorithms based on cross-validation Macro F1 performance
CHAMPIONS = {
    "behavioral_psychiatric": "logistic_regression",
    "bone_changes": "logistic_regression",
    "cardiovascular": "random_forest",
    "decompression_sickness": "decision_tree",
    "dynamic_load_injury": "random_forest",
    "food_nutrition": "logistic_regression",
    "host_microorganism": "logistic_regression",
    "hypoxia": "random_forest",
    "immune_system": "random_forest",
    "physical_fitness": "logistic_regression",
    "radiation_cancer": "decision_tree",
    "sans": "random_forest",
    "sensorimotor_vestibular": "logistic_regression",
    "sleep_irregularity": "logistic_regression",
    "spacewalk_injury": "random_forest",
    "systems_operations": "logistic_regression",
    "teamwork": "logistic_regression",
}

LABEL_NAMES = ["LOW", "MODERATE", "HIGH"]


class AstronautRiskTriageEngine:
    """
    Inference & Triage Engine for 17-Domain Astronaut Health Risk Monitoring.
    """

    def __init__(self, n_folds: int = 5):
        self.n_folds = n_folds
        self.domain_reverse_maps = self._build_reverse_maps()
        self.models = self._load_champion_models()

    def _build_reverse_maps(self) -> dict:
        """Construct dictionary mapping merged column names back to original domain feature names."""
        rev_maps = {}
        for path, cols, rmap in SOURCES:
            domain = path.stem
            rev_maps[domain] = {renamed: orig for orig, renamed in rmap.items()}
        return rev_maps

    def _load_champion_models(self) -> dict:
        """Load cross-validation fold models for all 17 champion algorithms into memory."""
        loaded = {}
        for domain, algo in CHAMPIONS.items():
            domain_models = []
            for fold in range(1, self.n_folds + 1):
                model_file = MODELS_DIR / domain / algo / f"fold_0{fold}.joblib"
                if not model_file.exists():
                    raise FileNotFoundError(f"Missing model binary: {model_file}")
                domain_models.append(joblib.load(model_file))
            loaded[domain] = domain_models
        return loaded

    def _prepare_domain_features(self, domain: str, row: pd.Series) -> pd.DataFrame:
        """Extract and align features required by a specific domain model."""
        feats = FEATURE_CONFIG[f"{domain}.csv"]
        rev_map = self.domain_reverse_maps.get(domain, {})

        data = {
            "mission_day": [row["mission_day"]],
            "mission_phase": [row["mission_phase"]],
        }

        for f in feats:
            # Prefer the domain-specific renamed source column when the same original
            # feature name occurs in multiple domains (e.g. HRV / microbial load).
            mapped = next((ren for ren, orig in rev_map.items() if orig == f and ren in row), None)
            if mapped is not None:
                data[f] = [row[mapped]]
            elif f in row:
                data[f] = [row[f]]
            else:
                raise ValueError(f"Missing required feature '{f}' for domain '{domain}'.")

        return pd.DataFrame(data)

    def predict_single_record(self, record: pd.Series) -> dict:
        """
        Run 17-domain ensemble inference on a single astronaut mission day.
        Returns detailed probability distributions, predictions, and triage alert level.
        """
        domain_results = {}
        high_risk_count = 0
        moderate_risk_count = 0

        for domain, fold_models in self.models.items():
            X = self._prepare_domain_features(domain, record)

            # 5-fold soft-voting ensemble
            fold_probs = [m.predict_proba(X)[0] for m in fold_models]
            avg_probs = np.mean(fold_probs, axis=0)

            # Ensure 3-class probability vector
            if len(avg_probs) < 3:
                full_probs = np.zeros(3)
                full_probs[: len(avg_probs)] = avg_probs
                avg_probs = full_probs

            pred_class = int(np.argmax(avg_probs))
            label = LABEL_NAMES[pred_class]
            confidence = float(avg_probs[pred_class])

            if pred_class == 2:
                high_risk_count += 1
            elif pred_class == 1:
                moderate_risk_count += 1

            domain_results[domain] = {
                "class": pred_class,
                "label": label,
                "confidence": confidence,
                "prob_low": float(avg_probs[0]),
                "prob_moderate": float(avg_probs[1]),
                "prob_high": float(avg_probs[2]),
                "algorithm": CHAMPIONS[domain],
            }

        # Overall Composite Mission Triage Index
        if high_risk_count >= 1:
            triage_status = "RED"
            triage_action = "CRITICAL ALERT: Clinical decompensation detected. Immediate flight surgeon intervention required."
        elif moderate_risk_count >= 1:
            triage_status = "AMBER"
            triage_action = "ELEVATED CONCERN: Sub-clinical strain detected. Increase monitoring and countermeasures."
        else:
            triage_status = "GREEN"
            triage_action = "NOMINAL: All 17 physiological and environmental domains within safe flight tolerances."

        # Rank top clinical threats (sorted by class descending, then high probability descending)
        ranked_threats = sorted(
            domain_results.items(),
            key=lambda item: (item[1]["class"], item[1]["prob_high"], item[1]["prob_moderate"]),
            reverse=True,
        )

        return {
            "astronaut_id": record.get("astronaut_id", "UNKNOWN"),
            "mission_day": int(record.get("mission_day", 0)),
            "mission_phase": record.get("mission_phase", "UNKNOWN"),
            "triage_status": triage_status,
            "triage_action": triage_action,
            "high_risk_count": high_risk_count,
            "moderate_risk_count": moderate_risk_count,
            "domain_predictions": domain_results,
            "top_threats": [
                {
                    "domain": item[0],
                    "label": item[1]["label"],
                    "confidence": item[1]["confidence"],
                    "prob_high": item[1]["prob_high"],
                }
                for item in ranked_threats[:3]
                if item[1]["class"] > 0
            ],
        }

    def predict_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run batch inference on multiple astronaut mission day records."""
        records = []
        for idx, row in df.iterrows():
            result = self.predict_single_record(row)
            flat = {
                "astronaut_id": result["astronaut_id"],
                "mission_day": result["mission_day"],
                "mission_phase": result["mission_phase"],
                "triage_status": result["triage_status"],
                "high_risk_count": result["high_risk_count"],
                "moderate_risk_count": result["moderate_risk_count"],
            }
            for domain, d_res in result["domain_predictions"].items():
                flat[f"{domain}_risk_class"] = d_res["class"]
                flat[f"{domain}_risk_label"] = d_res["label"]
                flat[f"{domain}_confidence"] = round(d_res["confidence"], 4)
                flat[f"{domain}_prob_high"] = round(d_res["prob_high"], 4)
            records.append(flat)

        return pd.DataFrame(records)


def print_triage_card(result: dict):
    """Render an astronaut-day clinical triage dashboard card."""
    ast_id = result["astronaut_id"]
    day = result["mission_day"]
    phase = result["mission_phase"]
    status = result["triage_status"]
    action = result["triage_action"]

    print("\n" + "=" * 78)
    print(f" NASA SPACE APPS - ASTRONAUT HEALTH RISK TRIAGE REPORT ")
    print("=" * 78)
    print(f"Astronaut ID:  {ast_id:<12} | Mission Day: Day {day:<5} | Phase: {phase}")
    print(f"Overall Status: [{status}]")
    print(f"Directive:      {action}")
    print("-" * 78)

    print(f"{'RISK DOMAIN':<32} {'MODEL':<18} {'LEVEL':<10} {'CONFIDENCE':<10} {'P(H)':<8}")
    print("-" * 78)

    for domain, res in result["domain_predictions"].items():
        dom_display = domain.replace("_", " ").title()
        algo = res["algorithm"].replace("_", " ").title()
        lbl = res["label"]
        conf = f"{res['confidence'] * 100:.1f}%"
        p_high = f"{res['prob_high'] * 100:.1f}%"
        print(f"{dom_display:<32} {algo:<18} {lbl:<10} {conf:<10} {p_high:<8}")

    print("-" * 78)
    if result["top_threats"]:
        print("TOP CLINICAL THREATS SURFACED:")
        for i, t in enumerate(result["top_threats"], 1):
            d_name = t["domain"].replace("_", " ").title()
            print(f"  {i}. {d_name}: {t['label']} (Confidence: {t['confidence']*100:.1f}%, P(High): {t['prob_high']*100:.1f}%)")
    else:
        print("TOP CLINICAL THREATS SURFACED: None (All systems nominal)")
    print("=" * 78 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="NASA Astronaut Health Risk Triage & Prediction CLI"
    )
    parser.add_argument(
        "--astronaut", type=str, default=None, help="Astronaut ID to query (e.g., AST002)"
    )
    parser.add_argument(
        "--day", type=int, default=None, help="Mission day to query (e.g., 95)"
    )
    parser.add_argument(
        "--input", type=str, default=None, help="Path to input CSV for batch risk prediction"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Path to save batch prediction results CSV"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run demonstrator queries (nominal day + EVA alert day)"
    )

    args = parser.parse_args()

    # Default to demo if no arguments provided
    if not args.astronaut and not args.input and not args.demo:
        args.demo = True

    print("Initializing Astronaut Risk Triage Engine...")
    triage_engine = AstronautRiskTriageEngine()

    if args.demo:
        print("\n[DEMO MODE] Running illustrative clinical triage scenarios...")
        if not INTEGRATED_DATASET_PATH.exists():
            print(f"Error: Integrated dataset not found at {INTEGRATED_DATASET_PATH}")
            return

        df_int = pd.read_csv(INTEGRATED_DATASET_PATH)

        # Scenario 1: Nominal Day (AST001, Day 15)
        row_nominal = df_int[(df_int["astronaut_id"] == "AST001") & (df_int["mission_day"] == 15)].iloc[0]
        res_nominal = triage_engine.predict_single_record(row_nominal)
        print_triage_card(res_nominal)

        # Scenario 2: High Operational Load / EVA Day (AST002, Day 95)
        row_eva = df_int[(df_int["astronaut_id"] == "AST002") & (df_int["mission_day"] == 95)].iloc[0]
        res_eva = triage_engine.predict_single_record(row_eva)
        print_triage_card(res_eva)

    elif args.astronaut and args.day:
        if not INTEGRATED_DATASET_PATH.exists():
            print(f"Error: Integrated dataset not found at {INTEGRATED_DATASET_PATH}")
            return
        df_int = pd.read_csv(INTEGRATED_DATASET_PATH)
        match = df_int[(df_int["astronaut_id"] == args.astronaut) & (df_int["mission_day"] == args.day)]
        if match.empty:
            print(f"Error: No record found for astronaut {args.astronaut} on Day {args.day}.")
            return
        result = triage_engine.predict_single_record(match.iloc[0])
        print_triage_card(result)

    elif args.input:
        in_path = Path(args.input)
        if not in_path.exists():
            print(f"Error: Input file does not exist: {in_path}")
            return
        df_in = pd.read_csv(in_path)
        print(f"Running batch prediction on {len(df_in)} records from {in_path}...")
        results_df = triage_engine.predict_dataframe(df_in)

        out_path = Path(args.output) if args.output else in_path.parent / f"{in_path.stem}_predictions.csv"
        results_df.to_csv(out_path, index=False)
        print(f"Batch predictions successfully saved to: {out_path}")


if __name__ == "__main__":
    main()
