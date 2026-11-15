# Database and source data

The backend uses SQLAlchemy with SQLite by default. On first launch it creates the schema and imports `seed/astronaut_health_integrated.csv` into `dataset_observations`. The importer is idempotent and stores each full 147-field row intact.

The original hazard and risk archives are preserved in `seed/source/`. See `../DATASET_VALIDATION.txt` and `../docs/DATA_DICTIONARY.md` for validation results and field mapping.
