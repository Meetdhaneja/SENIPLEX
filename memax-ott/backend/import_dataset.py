"""
Quick Dataset Import Script
Run this to import your dataset into the database
"""
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.data.loaders.load_to_db import import_dataset
from loguru import logger


def main():
    """Main import function"""
    print("=" * 60)
    print("MEMAX OTT - Dataset Import Tool")
    print("=" * 60)
    print()
    
    # Check for dataset file
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        print("Available dataset locations:")
        print("1. app/data/raw/")
        print("2. Custom path")
        print()
        
        # Check common locations
        common_paths = [
            "app/data/raw/netflix.csv",
            "app/data/raw/movies.csv",
            "app/data/raw/dataset.csv",
            "app/data/raw/netflix_titles.csv"
        ]
        
        found_datasets = []
        for path in common_paths:
            if os.path.exists(path):
                found_datasets.append(path)
        
        if found_datasets:
            print("Found datasets:")
            for i, path in enumerate(found_datasets, 1):
                size = os.path.getsize(path) / 1024 / 1024  # MB
                print(f"{i}. {path} ({size:.2f} MB)")
            print()
            
            choice = input(f"Select dataset (1-{len(found_datasets)}) or enter custom path: ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(found_datasets):
                    dataset_path = found_datasets[idx]
                else:
                    print("Invalid choice")
                    return
            except ValueError:
                dataset_path = choice
        else:
            dataset_path = input("Enter dataset file path: ").strip()
    
    # Verify file exists
    if not os.path.exists(dataset_path):
        print(f"❌ Error: File not found: {dataset_path}")
        print()
        print("Please place your dataset in one of these locations:")
        print("- app/data/raw/netflix.csv")
        print("- app/data/raw/movies.csv")
        print("Or provide the full path to your dataset file")
        return
    
    # Detect file type
    file_ext = Path(dataset_path).suffix.lower()
    if file_ext == '.csv':
        file_type = 'csv'
    elif file_ext == '.json':
        file_type = 'json'
    else:
        print(f"❌ Error: Unsupported file type: {file_ext}")
        print("Supported types: .csv, .json")
        return
    
    # Show file info
    file_size = os.path.getsize(dataset_path) / 1024 / 1024  # MB
    print()
    print(f"📁 Dataset: {dataset_path}")
    print(f"📊 Size: {file_size:.2f} MB")
    print(f"📝 Type: {file_type.upper()}")
    print()
    
    # Confirm import
    confirm = input("Start import? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Import cancelled")
        return
    
    print()
    print("🚀 Starting import...")
    print("-" * 60)
    
    try:
        # Import dataset
        count = import_dataset(dataset_path, file_type)
        
        print("-" * 60)
        print()
        print("✅ Import completed successfully!")
        print(f"📊 Total movies imported: {count}")
        print()
        print("Next steps:")
        print("1. Start the backend server: python -m app.main")
        print("2. Visit http://localhost:8000/docs to see the API")
        print("3. Start the frontend: cd ../frontend && npm run dev")
        print("4. Browse movies at http://localhost:3000")
        
    except Exception as e:
        print()
        print("❌ Import failed!")
        print(f"Error: {str(e)}")
        logger.exception("Import error")
        print()
        print("Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check database connection in .env file")
        print("3. Run: python -m app.db.init_db")
        print("4. Run: python -m app.db.seed")


if __name__ == "__main__":
    main()
