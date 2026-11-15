# Integrated dataset dictionary

The application imports `database/seed/astronaut_health_integrated.csv` without dropping columns. The file has 3,600 rows and 147 columns, with 20 astronaut IDs, one mission ID, 180 mission days per astronaut, and three mission phases.

## Row identity

- `astronaut_id`: AST001–AST020
- `mission_id`: SIM_MISSION_001
- `mission_day`: 1–180
- `mission_phase`: Outbound, Cruise, Return

## Five hazard domains

| Hazard | Representative source fields | Dataset category field |
|---|---|---|
| Space radiation | `radiation_rate_uGy_day`, `effective_dose_rate_uGy_day`, `cumulative_dose_uGy` | `radiation_alert` |
| Isolation and confinement | `sleep_duration_hours`, `sleep_quality_score`, `mood_score`, `isolation_stress_score` | `isolation_stress_level` |
| Distance from Earth | `distance_from_earth_km`, communication delays, `communication_outage`, `crew_autonomy_level` | `communication_risk_level` |
| Gravity fields | `gravity_level_g`, bone/muscle indices, fluid shift, balance and sensorimotor fields | `gravity_risk_level` |
| Hostile or closed environments | cabin CO₂/O₂, pressure, temperature, humidity, particulate and microbial fields | `environmental_alert_level` |

## Seventeen risk domains

| Risk domain | Category field | Score / exposure field |
|---|---|---|
| Altered immune system responses | `immune_risk_level` | `immune_risk_score` |
| Altered sensorimotor and vestibular function | `sensorimotor_risk_level` | `sensorimotor_risk_score` |
| Cardiovascular adaptations | `cardiovascular_risk_level` | `cardiovascular_risk_score` |
| Decompression sickness | `decompression_risk_level` | `decompression_exposure_score` |
| Host-microorganism interactions | `microorganism_risk_level` | `microorganism_risk_score` |
| Hypoxia | `hypoxia_risk_level` | `hypoxia_risk_score` |
| Inadequate food and nutrition | `nutrition_risk_level` | `nutrition_risk_score` |
| Injury and compromised performance from spacewalks | `spacewalk_injury_risk_level` | `spacewalk_injury_risk_score` |
| Reduced cardiorespiratory and musculoskeletal fitness | `fitness_risk_level` | `fitness_risk_score` |
| Spaceflight-associated neuro-ocular syndrome (SANS) | `sans_risk_level` | `sans_risk_score` |
| Spaceflight-induced bone changes | `bone_change_risk_level` | `bone_change_risk_score` |
| Behavioral changes and psychiatric disorders | `behavioral_risk_level` | `behavioral_risk_score` |
| Inadequate teamwork | `teamwork_risk_level` | `teamwork_risk_score` |
| Inadequate sleep and irregular schedules | `sleep_risk_level` | `sleep_risk_score` |
| Inadequate systems operations support | `systems_support_risk_level` | `systems_support_risk_score` |
| Injury from dynamic loads | `dynamic_load_risk_level` | `dynamic_load_risk_score` |
| Radiation-induced cancers | `radiation_cancer_exposure_category` | `long_term_radiation_exposure_index` |

## Storage strategy

`dataset_observations.payload_json` preserves every source field and value. Indexed identity fields (`crew_code`, `mission_code`, `mission_day`, `mission_phase`) support selection and chronological queries. Do not remap a field into another metric solely because its name or unit looks similar. For example, the dataset does not provide a direct body-temperature or blood-glucose field.

Risk category values are source labels. The UI displays them as labels; it does not translate them into diagnoses or clinical alert thresholds.
