"""Build movie embeddings"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.movie import Movie
from app.models.movie_embeddings import MovieEmbedding
from app.ai.embeddings.minilm_model import generate_embedding
from loguru import logger


def build_movie_embeddings():
    """Build embeddings for all movies"""
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        logger.info(f"Building embeddings for {len(movies)} movies")
        
        for movie in movies:
            # Create text representation
            # Check if exists
            movie_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == movie.id).first()
            if movie_emb and movie_emb.content_embedding:
                logger.debug(f"Skipping movie {movie.id}: Embedding already exists")
                continue
            
            # Create text representation
            text = f"{movie.title}. {movie.description or ''}. Genres: {', '.join([g.name for g in movie.genres])}"

            # Generate embedding
            embedding = generate_embedding(text)
            
            # Save or update
            movie_emb = db.query(MovieEmbedding).filter(MovieEmbedding.movie_id == movie.id).first()
            if movie_emb:
                movie_emb.content_embedding = embedding
            else:
                movie_emb = MovieEmbedding(movie_id=movie.id, content_embedding=embedding)
                db.add(movie_emb)
            
            db.commit()
        
        logger.info("Movie embeddings built successfully")
    except Exception as e:
        logger.error(f"Error building movie embeddings: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    build_movie_embeddings()
