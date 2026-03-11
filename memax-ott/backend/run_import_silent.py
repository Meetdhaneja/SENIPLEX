import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.data.loaders.load_to_db import import_dataset
import os

def main():
    dataset_path = os.path.join("app", "data", "raw", "Netflix_dataset_cleaned.csv")
    if not os.path.exists(dataset_path):
        print(f"❌ File not found: {dataset_path}")
        return

    print(f"🚀 Importing {dataset_path}...")
    try:
        count = import_dataset(dataset_path, 'csv')
        print(f"✅ Successfully imported {count} movies!")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
