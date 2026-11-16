# Synthetic dataset

**Generated for this assignment. Not collected from people, cameras, sensors, or any real facility.** Dataset title: *Northstar Station / Nightfall synthetic observations*, version 1, 2026. Generator: `../generate_data.py`; seed: **42**. Source attribution: project-specific, AI-assisted original fixture generation; see `../AI_PROMPTS.md`.

## Files

### `baseline.csv` — 1,000 rows

One header and 200 normal-reference rows per sensor bundle. Used only to fit Isolation Forest.

| Column | Type | Meaning |
|---|---|---|
| `sample_id` | string | Unique `BASE-0001` through `BASE-1000` |
| `source_id` | string | One of the five synthetic sensor bundle IDs |
| `zone` | string | A, B, C, or D |
| `voltage_v` | number | Voltage in volts; mean approximately 230 |
| `temperature_c` | number | Temperature in °C; mean approximately 22 |
| `particles_ug_m3` | number | Fictional particle concentration in µg/m³; mean approximately 9 |
| `vibration_mm_s` | number | Fictional vibration in mm/s; mean approximately 0.08 |

For each row, load L ~ Normal(0,1); independently drawn residuals give voltage = 230 + Normal(0,1.25) − 0.35L; temperature = 22 + Normal(0,0.55) + 0.25L; particles = 9 + Normal(0,1.25); vibration = 0.08 + Normal(0,0.006) + 0.002L. Values are rounded to three decimals except vibration (four). These are synthetic distributions, not equipment specifications or safety thresholds.

### `facility.json`

Contains `name`, `fictional`, `seed`, `coordinate_system`, four `zones`, explicit `adjacent_zones`, and eight `sources`. Each zone has an ID, display name, and rectangle geometry in **fictional SVG drawing units**. These are not latitude/longitude or a real site plan.

Each source has `id`, `zone`, `kind` (`sensor`, `camera`, `field`), and `name`. Sources: five multivariate sensor bundles, two authored camera-observation sources, and one fictional maintenance-log source. Both A sensor bundles include all four numeric features; they are simplified data bundles rather than detailed physical device models.

### `scenarios.json` — 3 scenarios × 14 events

Top-level array. Each scenario has `id`, `name`, `description`, `synthetic`, fictional `date`, and an ordered `events` array.

| Event field | Meaning |
|---|---|
| `id` | E01–E14, unique **within its scenario** |
| `seconds` | Offset from 22:14:00; integer, monotonically increasing |
| `time` | Fictional HH:MM:SS display time derived from the offset |
| `source_id`, `zone`, `kind` | Source reference and its location/type |
| `event_type` | `routine`, `power`, `visibility`, `equipment`, or `environment` |
| `title`, `message` | Authored display text |
| `stance` | Authored `neutral`, `support`, or `contradict`; used by rule-based scoring |
| `severity` | Authored numeric input, 0–1; not an ML prediction |
| `readings` | Sensor events only: the four feature/value pairs |
| `visual` | Camera events only: `haze`, `clear`, or `corridor` illustration label |

`analysis`, priorities, alerts, correlation links, and graph nodes/edges are **computed at runtime** and are not stored as ground-truth model outcomes in these input files. The UI's illustrative camera panel shows CAM-A1; CAM-B1's corridor observation can be inspected in the timeline.

## Regenerate

From the project root:

```sh
python3 generate_data.py
```
*Français : recrée les trois fichiers d'entrée synthétiques avec la même graine, sans dépendance externe.*

The generator requires only Python's standard library. The automated suite compares the generated files byte for byte with the checked-in inputs. No private file paths or external assets are required. Normal control events intentionally reuse nominal values for a clean educational comparison; they are not a realistic operational dataset. SHA-256 hashes of the actual inputs are included in every exported evidence file.
