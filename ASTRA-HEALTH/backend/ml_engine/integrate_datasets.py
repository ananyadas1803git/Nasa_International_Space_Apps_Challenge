"""
NASA Space Apps Challenge - Astronaut Health Risk Prediction
Module: integrate_datasets.py

Purpose:
    Integrates all 5 hazard-related datasets and 17 astronaut health risk datasets
    into a unified 3,600-row longitudinal master dataset (20 astronauts x 180 mission days).

    Upgrades in this revised version:
    1. Preserves exact 147-column schema compatibility with domain_constraints.json and downstream validators.
    2. Performs rigorous automated Cross-Domain Synchronization & Consistency Verification:
       - Confirms 100% exact event identity between decompression and injury spacewalk events.
       - Validates high cross-domain correlation across autonomic, sleep, muscular, and bio-burden streams.
    3. Generates detailed synchronization and dataset quality reports.
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
HAZARD_DIR = ROOT / "datasets" / "hazards"
RISK_DIR = ROOT / "datasets" / "risks"
OUTPUT_DIR = ROOT / "datasets" / "integrated"
VALIDATION_DIR = OUTPUT_DIR / "validation"
OUTPUT_FILE = OUTPUT_DIR / "astronaut_health_integrated.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

KEYS = ["astronaut_id", "mission_id", "mission_day"]

# Full 22 source dataset configurations with standard rename mapping
SOURCES = [
    # ----- 5 hazard datasets -----
    (HAZARD_DIR / "space_radiation.csv", [
        "mission_phase", "radiation_rate_uGy_day", "solar_particle_event",
        "shielding_effectiveness", "effective_dose_rate_uGy_day",
        "cumulative_dose_uGy", "radiation_alert",
    ], {}),
    (HAZARD_DIR / "isolation_confinement.csv", [
        "sleep_duration_hours", "sleep_quality_score",
        "heart_rate_variability_ms", "mood_score", "workload_hours",
        "social_interaction_hours", "isolation_stress_score",
        "isolation_stress_level",
    ], {
        "heart_rate_variability_ms": "isolation_heart_rate_variability_ms",
    }),
    (HAZARD_DIR / "distance_from_earth.csv", [
        "distance_from_earth_km", "one_way_communication_delay_seconds",
        "round_trip_communication_delay_seconds", "communication_outage",
        "crew_autonomy_level", "ground_support_score",
        "communication_risk_level",
    ], {}),
    (HAZARD_DIR / "gravity_fields.csv", [
        "gravity_level_g", "bone_density_index", "muscle_strength_index",
        "fluid_shift_score", "balance_coordination_score",
        "sensorimotor_symptom_score", "gravity_stress_score",
        "gravity_risk_level",
    ], {
        "muscle_strength_index": "gravity_muscle_strength_index",
    }),
    (HAZARD_DIR / "hostile_environment.csv", [
        "cabin_co2_ppm", "cabin_o2_percent", "cabin_pressure_kpa",
        "cabin_temperature_c", "cabin_humidity_percent",
        "particulate_concentration_index", "microbial_load_index",
        "environmental_stress_score", "environmental_alert_level",
    ], {
        "microbial_load_index": "environment_microbial_load_index",
    }),

    # ----- 17 risk datasets -----
    (RISK_DIR / "immune_system.csv", [
        "white_blood_cell_count", "inflammation_marker_index",
        "immune_response_index", "immune_risk_score", "immune_risk_level",
    ], {}),
    (RISK_DIR / "sensorimotor_vestibular.csv", [
        "balance_score", "coordination_score", "dizziness_score",
        "reaction_time_ms", "sensorimotor_risk_score",
        "sensorimotor_risk_level",
    ], {}),
    (RISK_DIR / "cardiovascular.csv", [
        "heart_rate_bpm", "systolic_bp_mmhg", "diastolic_bp_mmhg",
        "heart_rate_variability_ms", "cardiovascular_risk_score",
        "cardiovascular_risk_level",
    ], {
        "heart_rate_variability_ms": "cardiovascular_heart_rate_variability_ms",
    }),
    (RISK_DIR / "decompression_sickness.csv", [
        "spacewalk_event", "oxygen_prebreathing_minutes",
        "pressure_change_psi", "suit_pressure_psi",
        "decompression_exposure_score", "decompression_risk_level",
    ], {
        "spacewalk_event": "decompression_spacewalk_event",
    }),
    (RISK_DIR / "host_microorganism.csv", [
        "microbial_load_index", "surface_contamination_index",
        "immune_response_index", "hygiene_compliance_percent",
        "microorganism_risk_score", "microorganism_risk_level",
    ], {
        "microbial_load_index": "host_microorganism_load_index",
        "immune_response_index": "host_microorganism_immune_response_index",
    }),
    (RISK_DIR / "hypoxia.csv", [
        "cabin_oxygen_percent", "spo2_percent", "respiratory_rate_bpm",
        "hypoxia_risk_score", "hypoxia_risk_level",
    ], {}),
    (RISK_DIR / "food_nutrition.csv", [
        "calorie_target_kcal", "calorie_intake_kcal", "protein_intake_g",
        "water_intake_liters", "nutrition_status_index",
        "nutrition_risk_score", "nutrition_risk_level",
    ], {}),
    (RISK_DIR / "spacewalk_injury.csv", [
        "spacewalk_event", "eva_duration_minutes", "fatigue_score",
        "workload_score", "mobility_score", "spacewalk_injury_risk_score",
        "spacewalk_injury_risk_level",
    ], {
        "spacewalk_event": "injury_spacewalk_event",
        "fatigue_score": "spacewalk_fatigue_score",
    }),
    (RISK_DIR / "physical_fitness.csv", [
        "vo2_max_ml_kg_min", "muscle_strength_index", "endurance_index",
        "daily_exercise_hours", "fitness_risk_score", "fitness_risk_level",
    ], {
        "muscle_strength_index": "fitness_muscle_strength_index",
    }),
    (RISK_DIR / "sans.csv", [
        "intraocular_pressure_mmhg", "retinal_thickness_um",
        "visual_acuity_index", "vision_symptom_score",
        "sans_risk_score", "sans_risk_level",
    ], {}),
    (RISK_DIR / "bone_changes.csv", [
        "bone_mineral_density_g_cm3", "bone_resorption_marker_index",
        "serum_calcium_mg_dl", "resistance_exercise_hours",
        "bone_change_risk_score", "bone_change_risk_level",
    ], {}),
    (RISK_DIR / "behavioral_psychiatric.csv", [
        "stress_score", "anxiety_indicator_score", "mood_wellbeing_score",
        "motivation_score", "behavioral_risk_score", "behavioral_risk_level",
    ], {
        "stress_score": "behavioral_stress_score",
    }),
    (RISK_DIR / "teamwork.csv", [
        "communication_score", "cooperation_score",
        "crew_conflict_indicator", "task_coordination_score",
        "workload_imbalance_score", "teamwork_risk_score",
        "teamwork_risk_level",
    ], {}),
    (RISK_DIR / "sleep_irregularity.csv", [
        "sleep_duration_hours", "sleep_quality_score",
        "schedule_irregularity_score", "circadian_disruption_score",
        "sleep_risk_score", "sleep_risk_level",
    ], {
        "sleep_duration_hours": "sleep_risk_sleep_duration_hours",
        "sleep_quality_score": "sleep_risk_sleep_quality_score",
    }),
    (RISK_DIR / "systems_operations.csv", [
        "equipment_reliability_percent", "maintenance_delay_hours",
        "ground_support_availability_percent", "system_failure_event",
        "procedure_deviation_score", "systems_support_risk_score",
        "systems_support_risk_level",
    ], {}),
    (RISK_DIR / "dynamic_load_injury.csv", [
        "acceleration_g", "load_factor", "movement_frequency_score",
        "fatigue_score", "restraint_effectiveness_percent",
        "dynamic_load_risk_score", "dynamic_load_risk_level",
    ], {
        "fatigue_score": "dynamic_load_fatigue_score",
    }),
    (RISK_DIR / "radiation_cancer.csv", [
        "radiation_rate_mSv_day", "cumulative_radiation_mSv",
        "shielding_factor", "relative_susceptibility_factor",
        "long_term_radiation_exposure_index",
        "radiation_cancer_exposure_category",
    ], {}),
]


def load_one(path: Path, selected_columns: list[str], rename_map: dict) -> pd.DataFrame:
    """Load a single generator dataset, validate keys, and apply rename map."""
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input dataset: {path}\n"
            "Ensure hazard and risk CSV files are generated first."
        )

    frame = pd.read_csv(path)

    missing_keys = [col for col in KEYS if col not in frame.columns]
    if missing_keys:
        raise ValueError(f"{path.name} is missing join keys: {missing_keys}")

    missing_features = [col for col in selected_columns if col not in frame.columns]
    if missing_features:
        raise ValueError(f"{path.name} is missing expected columns: {missing_features}")

    frame = frame[KEYS + selected_columns].copy()

    if frame[KEYS].isna().any().any():
        raise ValueError(f"{path.name} contains missing join-key values.")

    if frame.duplicated(KEYS).any():
        raise ValueError(f"{path.name} contains duplicate astronaut/mission/day keys.")

    # Retain mission_phase from the first source only
    if "mission_phase" in frame.columns and path.name != "space_radiation.csv":
        frame = frame.drop(columns=["mission_phase"])

    return frame.rename(columns=rename_map)


def verify_cross_domain_synchronization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automated check verifying that related cross-domain streams agree:
    1. Spacewalk events have 100% exact boolean identity.
    2. Autonomic HRV, sleep, microbial, and muscle streams exhibit strong positive correlation.
    """
    print("\n" + "=" * 65)
    print("RUNNING CROSS-DOMAIN SYNCHRONIZATION VERIFICATION")
    print("=" * 65)

    checks = []

    # 1. Spacewalk Event Boolean Identity
    if "decompression_spacewalk_event" in df.columns and "injury_spacewalk_event" in df.columns:
        mismatches = int((df["decompression_spacewalk_event"] != df["injury_spacewalk_event"]).sum())
        checks.append({
            "check": "Spacewalk Event Identity",
            "stream_a": "decompression_spacewalk_event",
            "stream_b": "injury_spacewalk_event",
            "metric": "Exact Match %",
            "value": f"{(1.0 - mismatches / len(df)) * 100:.2f}%",
            "status": "PASS" if mismatches == 0 else f"FAIL ({mismatches} mismatches)"
        })

    # 2. Autonomic HRV Correlation
    if "cardiovascular_heart_rate_variability_ms" in df.columns and "isolation_heart_rate_variability_ms" in df.columns:
        r_hrv = df["cardiovascular_heart_rate_variability_ms"].corr(df["isolation_heart_rate_variability_ms"])
        checks.append({
            "check": "Autonomic HRV Consistency",
            "stream_a": "cardiovascular_hrv",
            "stream_b": "isolation_hrv",
            "metric": "Pearson Correlation (r)",
            "value": f"{r_hrv:.3f}",
            "status": "PASS" if r_hrv > 0.85 else "WARN"
        })

    # 3. Sleep Duration Consistency
    if "sleep_duration_hours" in df.columns and "sleep_risk_sleep_duration_hours" in df.columns:
        r_sleep = df["sleep_duration_hours"].corr(df["sleep_risk_sleep_duration_hours"])
        checks.append({
            "check": "Sleep Duration Consistency",
            "stream_a": "isolation_sleep_hours",
            "stream_b": "sleep_risk_sleep_hours",
            "metric": "Pearson Correlation (r)",
            "value": f"{r_sleep:.3f}",
            "status": "PASS" if r_sleep > 0.85 else "WARN"
        })

    # 4. Microbial Bio-Burden Consistency
    if "environment_microbial_load_index" in df.columns and "host_microorganism_load_index" in df.columns:
        r_microbe = df["environment_microbial_load_index"].corr(df["host_microorganism_load_index"])
        checks.append({
            "check": "Microbial Load Consistency",
            "stream_a": "environment_microbial_load",
            "stream_b": "host_microbial_load",
            "metric": "Pearson Correlation (r)",
            "value": f"{r_microbe:.3f}",
            "status": "PASS" if r_microbe > 0.80 else "WARN"
        })

    # 5. Muscle Strength Consistency
    if "gravity_muscle_strength_index" in df.columns and "fitness_muscle_strength_index" in df.columns:
        r_muscle = df["gravity_muscle_strength_index"].corr(df["fitness_muscle_strength_index"])
        checks.append({
            "check": "Musculoskeletal Strength Consistency",
            "stream_a": "gravity_muscle_strength",
            "stream_b": "fitness_muscle_strength",
            "metric": "Pearson Correlation (r)",
            "value": f"{r_muscle:.3f}",
            "status": "PASS" if r_muscle > 0.85 else "WARN"
        })

    report_df = pd.DataFrame(checks)
    print(report_df.to_string(index=False))

    report_path = VALIDATION_DIR / "cross_domain_synchronization_report.csv"
    report_df.to_csv(report_path, index=False)
    print(f"\nSaved synchronization report to: {report_path}")

    return report_df


def main():
    integrated = None
    source_row_counts = []

    print("\nIntegrating 22 hazard and risk datasets...")
    for path, columns, rename_map in SOURCES:
        current = load_one(path, columns, rename_map)
        source_row_counts.append((path.name, len(current)))

        if integrated is None:
            integrated = current
        else:
            integrated = integrated.merge(
                current,
                on=KEYS,
                how="outer",
                validate="one_to_one",
            )

    if integrated is None:
        raise RuntimeError("No source datasets were configured.")

    integrated = integrated.sort_values(
        ["astronaut_id", "mission_day"]
    ).reset_index(drop=True)

    # Basic structural validation
    if integrated.duplicated(KEYS).any():
        raise ValueError("Integrated output contains duplicate join keys.")

    if len(integrated) != 20 * 180:
        raise ValueError(f"Expected 3,600 rows (20 astros x 180 days), got {len(integrated)}.")

    print(f"Integration complete: {len(integrated)} rows x {len(integrated.columns)} columns.")
    print(f"Unique astronauts: {integrated['astronaut_id'].nunique()} | Mission Days: {integrated['mission_day'].min()}-{integrated['mission_day'].max()}")
    print(f"Missing cells: {int(integrated.isna().sum().sum())}")

    # Run cross-domain synchronization check
    sync_report = verify_cross_domain_synchronization(integrated)

    # Save integrated dataset
    integrated.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved integrated dataset to:\n{OUTPUT_FILE}")

    # Save updated data-quality report
    quality = pd.DataFrame({
        "column": integrated.columns,
        "dtype": [str(dtype) for dtype in integrated.dtypes],
        "missing_count": [int(integrated[col].isna().sum()) for col in integrated.columns],
        "missing_percent": [
            round(integrated[col].isna().mean() * 100, 2)
            for col in integrated.columns
        ],
        "unique_values": [int(integrated[col].nunique(dropna=True)) for col in integrated.columns],
    })
    quality.to_csv(OUTPUT_DIR / "integrated_dataset_quality_report.csv", index=False)
    print("Saved integrated_dataset_quality_report.csv successfully.")


if __name__ == "__main__":
    main()
