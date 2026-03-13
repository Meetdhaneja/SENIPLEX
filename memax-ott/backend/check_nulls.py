import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:Meet%40123@localhost:5432/Netflix")

with engine.connect() as connection:
    result = connection.execute(text("SELECT count(*) FROM movies WHERE thumbnail_url IS NULL"))
    null_count = result.scalar()
    print(f"NULL_POSTERS: {null_count}")
