import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:Meet%40123@localhost:5432/Netflix")

with engine.connect() as connection:
    # Check how many have placeholders vs real URLs
    result = connection.execute(text("SELECT count(*) FROM movies WHERE thumbnail_url LIKE '%placeholder.com%'"))
    placeholders = result.scalar()
    
    result = connection.execute(text("SELECT count(*) FROM movies WHERE thumbnail_url LIKE 'http%' AND thumbnail_url NOT LIKE '%placeholder.com%'"))
    real_posters = result.scalar()
    
    print(f"--- POSTER_REPORT_START ---")
    print(f"TOTAL_MOVIES: {placeholders + real_posters}")
    print(f"REAL_POSTERS: {real_posters}")
    print(f"PLACEHOLDERS: {placeholders}")
    print(f"--- POSTER_REPORT_END ---")
