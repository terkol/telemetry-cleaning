# Industrial Telemetry ETL

This repository contains a data engineering pipeline designed to ingest, validate, and route raw IoT  telemetry from industrial bioreactors, for example. 

## The Objective

Industrial sensor data is chaotic and suffers from asynchronous sampling, hardware failures, and network packet loss. Standard data science pipelines like to rely on downstream imputation (like replacing anomalies with rolling averages), which masks hardware degradation and creates "Silent Failures."

This pipeline implements a Dead Letter Queue (DLQ) architecture. It prioritizes data lineage by applying strict physical and chemical boundary constraints at the point of ingestion. Clean data is routed to a clean database, while anomalous data is routed into a JSON log. 

## Data Provenance

Because publicly available datasets are often pre-cleaned for academic machine learning tasks, the telemetry data used in this repository (`dirty_bioreactor_telemetry.csv`) was synthetically generated via an LLM. 

It was deliberately made to inject specific, critical edge cases potentially found in real IoT environments to stress test the pipeline's fault tolerance, including:

* Varying time formats (mixed Unix epoch, ISO 8601, and missing timestamps)
* Type mismatches (e.g., reboot strings in float columns)
* Physical "impossibilities" (e.g., pH > 14, water temperatures exceeding boiling points in 1 bar pressure)

## Architecture & Stack
### Data I/O: 

`pandas` (Reading the raw CSV telemetry).

### Validation Engine:

`pydantic` (Enforces a strict schema and physical boundaries).

### Iteration: 
Native Python dictionary iteration (`to_dict('records')`) to bypass Pandas row iteration bottlenecks during the validation loop.

## Domain Constraints

The pipeline enforces the following physical boundaries for a toy aqueous bioreactor system. Any row violating these constraints is automatically quarantined:
* Temperature: 0.0°C to 100.0°C (Liquid water constraints)
* pH Level: 0.0 to 14.0 (Standard chemical scale)
* Pressure: 0.0 to 100.0 PSI (Structural tank limits)

## Installation & Execution

The pipeline can be executed manually or with Docker.

### Manual method:

Install the requirements (pandas, pydantic):

`pip install -r requirements.txt`

Execute the pipeline on the raw telemetry file:

`python telemetry_cleaning.py`

### Docker method

This repository has a Dockerfile to ensure it runs consistently across environments. This was my first time implementing containerization, so I focused on using industry standards like layer caching and non-root users to learn the "production" way of shipping code. 

From the project root, build the "telemetry-etl" image:

`docker build -t telemetry-etl .`

To write the output files back to the local `data/` folder, run:

`docker run --rm -v "$(pwd)/data:/app/data" telemetry-etl`

## Pipeline Outputs

The script consumes `data/dirty_bioreactor_telemetry.csv` and automatically directs the data into two separate files:

### `data/clean_telemetry.csv`:

The validated, production-ready dataset. All timestamps are verified, data types are locked, and  anomalies have been removed. Ready for downstream Machine Learning models. 

### `data/validation_report.json` (The Dead Letter Queue):

A structured diagnostic log detailing why specific rows were rejected.
