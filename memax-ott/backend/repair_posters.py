import pandas as pd
import sys
import os
import random
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from sqlalchemy import create_engine, text

# Add project root
sys.path.append(os.getcwd())

# Configuration
CSV_PATH = "app/data/raw/Netflix_dataset_cleaned.csv"
DB_URL = "postgresql://postgres:Meet%40123@localhost:5432/Netflix"
POSTER_LIMIT = 600

try:
    import movieposters as mp
except ImportError:
    mp = None

def get_poster(title):
    if not mp: return None
    try:
        # Search for poster
        posters = mp.get_poster(title=title)
        return posters if isinstance(posters, str) else None
    except:
        return None

def repair():
    if not os.path.exists(CSV_PATH):
        logger.error(f"CSV not found at {CSV_PATH}")
        return

    logger.info("Reading CSV...")
    df = pd.read_csv(CSV_PATH)
    rows = df.to_dict('records')
    
    engine = create_engine(DB_URL)
    
    # 1. Fetch real posters for the top rows
    logger.info(f"Fetching real posters for top {POSTER_LIMIT} titles...")
    poster_map = {}
    titles_to_fetch = [r.get('title') for r in rows[:POSTER_LIMIT]]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_poster, t): t for t in titles_to_fetch}
        for i, future in enumerate(futures):
            title = futures[future]
            try:
                res = future.result(timeout=10)
                if res:
                    poster_map[title] = res
            except Exception:
                pass
            if i % 50 == 0:
                logger.info(f"Checked {i} titles for posters...")

    logger.info(f"Successfully found {len(poster_map)} real posters.")

    # 2. Update DB in batches
    logger.info("Updating database thumbnails...")
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            for i, row in enumerate(rows):
                title = row.get('title')
                if not title: continue
                
                # Determine URL
                if title in poster_map:
                    url = poster_map[title]
                else:
                    # Generic placeholder
                    url = f"https://via.placeholder.com/400x600/111/eee?text={title[:20].replace(' ', '+')}"
                
                # Update query
                conn.execute(
                    text("UPDATE movies SET thumbnail_url = :url WHERE title = :title AND thumbnail_url IS NULL"),
                    {"url": url, "title": title}
                )
                
                if i % 500 == 0:
                    logger.info(f"Processed {i} titles...")
            
            transaction.commit()
            logger.info("Database update complete!")
        except Exception as e:
            transaction.rollback()
            logger.error(f"Error during update: {e}")

if __name__ == "__main__":
    repair()
