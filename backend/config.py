from pathlib import Path

# Automatically detect 'sumarg/' root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Simulation Paths
SIM_CONFIG_PATH = ROOT_DIR / "simulation" / "osm.sumocfg"

# ML Engine Paths
DATASET_CSV_PATH = ROOT_DIR / "ml_engine" / "datasets" / "braking_data.csv"
BRAKE_MODEL_PATH = ROOT_DIR / "ml_engine" / "saved_models" / "brake_model.pkl"

# Ego Vehicle Constants
EGO_VEHICLE_ID = "ego_car"
MAX_SPEED = 22.0  # ~80 km/h
