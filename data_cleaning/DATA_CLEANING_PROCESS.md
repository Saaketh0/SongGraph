# Data Cleaning Process

## Goal
Build a cleaned Spotify-style song dataset with:
- invalid values corrected
- structured missingness preserved via `_missing` flags
- key audio features imputed
- duplicate `track_id` rows removed
- final output ready for downstream modeling/graph work

## Starting Point
- Began from the pre-imputation cleaned parquet.
- Added missingness flags for the modeling feature set so downstream models could distinguish observed values from imputed values.

## Feature Imputation Strategy
- Used separate XGBoost models per target column rather than one multi-target model.
- Regression targets:
  - `valence`
  - `loudness`
  - `danceability`
  - `energy`
  - `acousticness`
  - `instrumentalness`
  - `liveness`
  - `speechiness`
  - later `tempo`
- Classification targets:
  - `mode`
  - `key`

## Modeling Approach
- Evaluated each target on rows where the target was originally observed.
- Used train/test splits and cross-validation during experimentation.
- Kept `_missing` flags in the feature set to preserve structured missingness information.
- Avoided global MICE-style iterative imputation because the dataset was large and missingness was highly structured.

## Important Target-Specific Findings
- `energy`: some missing rows had no usable predictors at all, so those rows were removed from the dataset instead of being imputed.
- `loudness`: worked well once regression clipping to `[0, 1]` was removed.
- `acousticness`, `speechiness`, `instrumentalness`, `liveness`, `valence`: imputed with XGBoost regression and retained their `_missing` flags.
- `tempo`: imputed last; model quality was weaker than the other numeric targets but all missing values were filled.
- `mode`: binary classifier tended to push the missing-row subgroup strongly toward `1`; multiple weighting/threshold experiments were tested, but no materially better replacement was adopted.
- `key`: standard classifier was improved slightly by a custom geometric-loss approach that penalized far musical mistakes more than near ones. That final geometric model was used to fill missing `key` values.

## Key-Specific Experiments
- Tested:
  - plain classifier
  - distance-aware decoding
  - confidence-gated decoding
  - 3D regression formulation
  - weighted retraining
  - key-only geometric-loss classifier
- The best result came from the key-only geometric-loss classifier with:
  - chromatic ordering
  - Gaussian-squared distance kernel
  - `alpha = 0.4`
  - `beta = 2.0`
- That model was then fit on all observed `key` rows and used to fill missing `key`.

## Dataset Consolidation
- Built progressive final parquets during the process:
  - `finalv1.parquet`: key-imputed version
  - `finalv2.parquet`: tempo-imputed version
  - `finalv3.parquet`: postprocessed version

## Final Structural Cleanup
- Removed rows with blank `track_name`.
- Deduplicated repeated non-empty `track_id` rows by keeping the most complete row and breaking ties by original row order.
- Cast:
  - `key` to `int8`
  - `mode` to `int8`
- Normalized `artist_name` conservatively:
  - trimmed whitespace
  - normalized semicolon spacing
  - removed full bracket wrappers like `[name] -> name`
  - did not attempt aggressive artist-name inference/filling

## Final Dataset State
- Audio/model features are fully filled.
- Remaining missingness is metadata only:
  - `track_id`
  - `artist_name`
- `_missing` flag columns were intentionally kept.
- `finalv3.parquet` is the latest cleaned dataset before final rename/move.
