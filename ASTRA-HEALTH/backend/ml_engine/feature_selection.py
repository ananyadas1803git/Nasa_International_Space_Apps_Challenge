"""
feature_selection.py

Purpose:
    Select relevant predictors for all 17 astronaut health risks.

Input:
    datasets/ml_ready/encoded_targets/*.csv

Output:
    datasets/ml_ready/feature_selected/*.csv
    datasets/ml_ready/feature_selection_report.csv

Important:
    Risk scores and risk labels are excluded from input features
    to prevent direct target leakage.
"""

from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = (
    BASE_DIR / "datasets" / "ml_ready" / "encoded_targets"
)

OUTPUT_DIR = (
    BASE_DIR / "datasets" / "ml_ready" / "feature_selected"
)

REPORT_PATH = (
    BASE_DIR / "datasets" / "ml_ready"
    / "feature_selection_report.csv"
)


# ---------------------------------------------------------
# COMMON METADATA
# ---------------------------------------------------------

# These columns are retained for traceability but are not
# included as model predictors.

METADATA_COLUMNS = [
    "astronaut_id",
    "mission_id"
]

# These can be used as predictors.
CONTEXT_FEATURES = [
    "mission_day",
    "mission_phase"
]


# ---------------------------------------------------------
# RISK-SPECIFIC FEATURE CONFIGURATION
# ---------------------------------------------------------

FEATURE_CONFIG = {

    "behavioral_psychiatric.csv": [

        "stress_score",
        "anxiety_indicator_score",
        "mood_wellbeing_score",
        "motivation_score"

    ],

    "bone_changes.csv": [

        "bone_mineral_density_g_cm3",
        "bone_resorption_marker_index",
        "serum_calcium_mg_dl",
        "resistance_exercise_hours"

    ],

    "cardiovascular.csv": [

        "heart_rate_bpm",
        "systolic_bp_mmhg",
        "diastolic_bp_mmhg",
        "heart_rate_variability_ms"

    ],

    "decompression_sickness.csv": [

        "spacewalk_event",
        "oxygen_prebreathing_minutes",
        "pressure_change_psi",
        "suit_pressure_psi"

    ],

    "dynamic_load_injury.csv": [

        "acceleration_g",
        "load_factor",
        "movement_frequency_score",
        "fatigue_score",
        "restraint_effectiveness_percent"

    ],

    "food_nutrition.csv": [

        "calorie_target_kcal",
        "calorie_intake_kcal",
        "protein_intake_g",
        "water_intake_liters",
        "nutrition_status_index"

    ],

    "host_microorganism.csv": [

        "microbial_load_index",
        "surface_contamination_index",
        "immune_response_index",
        "hygiene_compliance_percent"

    ],

    "hypoxia.csv": [

        "cabin_oxygen_percent",
        "spo2_percent",
        "respiratory_rate_bpm"

    ],

    "immune_system.csv": [

        "white_blood_cell_count",
        "inflammation_marker_index",
        "immune_response_index"

    ],

    "physical_fitness.csv": [

        "vo2_max_ml_kg_min",
        "muscle_strength_index",
        "endurance_index",
        "daily_exercise_hours"

    ],

    "radiation_cancer.csv": [

        "radiation_rate_mSv_day",
        "cumulative_radiation_mSv",
        "shielding_factor",
        "relative_susceptibility_factor",
        "long_term_radiation_exposure_index"

    ],

    "sans.csv": [

        "intraocular_pressure_mmhg",
        "retinal_thickness_um",
        "visual_acuity_index",
        "vision_symptom_score"

    ],

    "sensorimotor_vestibular.csv": [

        "balance_score",
        "coordination_score",
        "dizziness_score",
        "reaction_time_ms"

    ],

    "sleep_irregularity.csv": [

        "sleep_duration_hours",
        "sleep_quality_score",
        "schedule_irregularity_score",
        "circadian_disruption_score"

    ],

    "spacewalk_injury.csv": [

        "spacewalk_event",
        "eva_duration_minutes",
        "fatigue_score",
        "workload_score",
        "mobility_score"

    ],

    "systems_operations.csv": [

        "equipment_reliability_percent",
        "maintenance_delay_hours",
        "ground_support_availability_percent",
        "system_failure_event",
        "procedure_deviation_score"

    ],

    "teamwork.csv": [

        "communication_score",
        "cooperation_score",
        "crew_conflict_indicator",
        "task_coordination_score",
        "workload_imbalance_score"

    ]

}


# ---------------------------------------------------------
# FEATURE SELECTION FUNCTION
# ---------------------------------------------------------

def select_features():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report_records = []

    print("\n" + "=" * 65)
    print("ASTRONAUT HEALTH FEATURE SELECTION")
    print("=" * 65)

    for filename, risk_features in FEATURE_CONFIG.items():

        input_path = INPUT_DIR / filename

        if not input_path.exists():

            print(
                f"\n[WARNING] Encoded dataset missing: {filename}"
            )

            continue

        df = pd.read_csv(input_path)

        print(f"\nProcessing: {filename}")

        # Validate target
        required_target_columns = [
            "target",
            "target_label"
        ]

        missing_targets = [
            col for col in required_target_columns
            if col not in df.columns
        ]

        if missing_targets:

            raise ValueError(
                f"Missing target columns in {filename}: "
                f"{missing_targets}"
            )

        # Validate selected features
        missing_features = [
            feature for feature in risk_features
            if feature not in df.columns
        ]

        if missing_features:

            raise ValueError(
                f"Missing predictors in {filename}: "
                f"{missing_features}"
            )

        # Add available context features
        selected_features = (
            CONTEXT_FEATURES.copy()
        )

        selected_features = [
            feature for feature in selected_features
            if feature in df.columns
        ]

        selected_features.extend(risk_features)

        # Remove accidental duplicates
        selected_features = list(
            dict.fromkeys(selected_features)
        )

        # Check that score/label columns are not predictors
        leakage_features = [
            col for col in selected_features
            if "risk_score" in col.lower()
            or "risk_level" in col.lower()
            or col == "radiation_cancer_exposure_category"
        ]

        if leakage_features:

            raise ValueError(
                f"Potential target leakage in {filename}: "
                f"{leakage_features}"
            )

        # Keep identifiers separately for traceability
        metadata = [
            col for col in METADATA_COLUMNS
            if col in df.columns
        ]

        # Construct ML-ready dataset
        output_columns = (
            metadata
            + selected_features
            + ["target_label", "target"]
        )

        ml_df = df[output_columns].copy()

        # Save dataset
        output_path = OUTPUT_DIR / filename

        ml_df.to_csv(
            output_path,
            index=False
        )

        # Generate feature selection report
        for feature in selected_features:

            report_records.append({

                "dataset": filename,

                "feature": feature,

                "feature_type": (
                    "context"
                    if feature in CONTEXT_FEATURES
                    else "risk_predictor"
                ),

                "is_target": False,

                "is_metadata": False

            })

        for column in metadata:

            report_records.append({

                "dataset": filename,

                "feature": column,

                "feature_type": "metadata",

                "is_target": False,

                "is_metadata": True

            })

        report_records.append({

            "dataset": filename,

            "feature": "target",

            "feature_type": "target",

            "is_target": True,

            "is_metadata": False

        })

        print("Original columns:", len(df.columns))

        print("Selected predictors:", len(selected_features))

        print("Metadata columns:", metadata)

        print("Final ML dataset shape:", ml_df.shape)

        print(
            "[SUCCESS] Saved:",
            output_path
        )

    # Save report
    report_df = pd.DataFrame(report_records)

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report_df.to_csv(
        REPORT_PATH,
        index=False
    )

    print("\n" + "=" * 65)
    print("FEATURE SELECTION COMPLETED")
    print("=" * 65)

    print("Feature selection report:", REPORT_PATH)

    print("Output directory:", OUTPUT_DIR)


# ---------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------

if __name__ == "__main__":

    select_features()