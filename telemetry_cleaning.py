import pandas as pd
import json
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from pathlib import Path

class BioreactorReading(BaseModel):
    timestamp: datetime
    sensor_id: str
    temperature_c: float = Field(ge=0.0, le=100.0) 
    ph_level: float = Field(ge=0.0, le=14.0)       
    pressure_psi: float = Field(ge=0.0, le=100.0)  

def process_telemetry(file_path: str):
    print("Loading raw telemetry...")
    path = Path(__file__).parent / 'data'
    df = pd.read_csv(path / file_path)

    raw_records = df.to_dict('records')
    clean_data = []
    error_log = []
    
    print(f"Beginning validation of {len(raw_records)} records...")
    
    for i, record in enumerate(raw_records):
        try:
            valid_model = BioreactorReading(**record)
            
            clean_data.append(valid_model.model_dump())
            
        except ValidationError as e:
            error_log.append({
                "row_index": i,
                "raw_data": record,
                "errors": e.errors()
            })
            
    print(f"Validation Complete. Valid Rows: {len(clean_data)} | Anomalies: {len(error_log)}")
    
    if clean_data:
        clean_df = pd.DataFrame(clean_data)
        clean_df.to_csv(path / "clean_telemetry.csv", index=False)
        
    if error_log:
        with open(path / "validation_report.json", "w") as f:
            json.dump(error_log, f, indent=4)

if __name__ == '__main__':
    process_telemetry("dirty_bioreactor_telemetry.csv")