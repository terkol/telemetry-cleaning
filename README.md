# Industrial Telemetry ETL: Resilient Data Ingestion Pipeline

This repository contains a robust Data Engineering pipeline designed to ingest, validate, and route raw, error-prone IoT sensor telemetry from industrial bioreactors. 

## The Objective
Industrial sensor data is inherently chaotic, suffering from asynchronous sampling, hardware failures, and network packet loss. Standard data science pipelines often rely on downstream imputation (like replacing anomalies with rolling averages), which masks hardware degradation and creates "Silent Failures."

This pipeline implements a strict Dead Letter Queue (DLQ) Architecture. It prioritizes data lineage by enforcing physical and chemical boundary constraints at the point of ingestion. Valid data is routed to a clean database, while anomalous data is quarantined into a diagnostic JSON log for hardware maintenance review.

## Data Provenance & Synthetic Stress-Testing
Because publicly available industrial datasets are often aggressively pre-cleaned for academic machine learning tasks, the telemetry data used in this repository (`dirty_bioreactor_telemetry.csv`) was synthetically generated via an LLM. 

It was deliberately engineered to inject specific, critical edge cases found in real-world IoT environments to stress-test the pipeline's fault tolerance, including:
* Temporal chaos (mixed Unix epoch, ISO 8601, and missing timestamps)
* Type mismatches (e.g., reboot strings in float columns)
* Physical impossibilities (e.g., pH > 14, temperatures exceeding boiling points)

## Architecture & Stack
### Data I/O: 
`pandas` (Optimized for rapid loading of raw CSV telemetry).

### Validation Engine:

`pydantic` (Enforces strict schema compliance and physical boundaries).

### Iteration: 
Native Python dictionary iteration (`to_dict('records')`) to bypass Pandas row-iteration bottlenecks during the validation loop.

## Domain Constraints (Pydantic Schema)
The pipeline enforces the following physical boundaries for a toy aqueous bioreactor system. Any row violating these constraints is automatically quarantined:
* **Temperature:** 0.0°C to 100.0°C (Liquid water constraints)
* **pH Level:** 0.0 to 14.0 (Standard chemical scale)
* **Pressure:** 0.0 to 100.0 PSI (Structural tank limits)

## Installation & Execution

Install the requirements (pandas, pydantic):

`pip install -r requirements.txt`

Execute the pipeline on the raw telemetry file:

`python telemetry_cleaning.py`

## Pipeline Outputs

The script consumes `dirty_bioreactor_telemetry.csv` and automatically routes the data into two distinct artifacts:

### `clean_telemetry.csv`:

The validated, production-ready dataset. All timestamps are verified, data types are locked, and  anomalies have been removed. Ready for downstream Machine Learning models or BI dashboards.

### `validation_report.json` (The Dead Letter Queue):

A structured diagnostic log detailing why specific rows were rejected.

Example DLQ Entry:

```
{
    "row_index": 7,
    "raw_data": {
        "timestamp": "2026-05-04T10:06:00Z",
        "sensor_id": "BIO_TANK_1",
        "temperature_c": 37.2,
        "ph_level": 18.5,
        "pressure_psi": 15.1
    },
    "errors": [
        {
            "loc": ["ph_level"],
            "msg": "Input should be less than or equal to 14.0",
            "type": "less_than_equal"
        }
    ]
}
```