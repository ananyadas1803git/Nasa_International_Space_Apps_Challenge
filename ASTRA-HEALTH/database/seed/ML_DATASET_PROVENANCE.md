# Dataset provenance

The application canonical seed `astronaut_health_integrated.csv` is copied from the ML team's handover at `datasets/integrated/astronaut_health_integrated.csv`. It supersedes the older integrated CSV that was bundled in the previous application archive. The schema remains 3,600 rows × 147 columns; astronaut IDs, mission IDs, mission days and mission phases align, while many measurement values and source risk labels have been updated. This ensures the application dashboard and ML inference prefill use the same current dataset snapshot as the ML handover.

The observations are simulated/research-style data, not real astronaut medical records.
