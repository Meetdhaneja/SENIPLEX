import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:Meet%40123@localhost:5432/Netflix")

with engine.connect() as connection:
    result = connection.execute(text("SELECT title, thumbnail_url FROM movies LIMIT 5"))
    for row in result:
        print(f"TITLE: {row[0]} | URL: {row[1]}")
