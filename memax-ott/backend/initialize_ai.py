"""
Initialize All AI Models and Components
This script pre-loads all AI models, builds FAISS index, and prepares the system
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from loguru import logger
import time

logger.info("=" * 60)
logger.info("MEMAX OTT - AI Initialization")
logger.info("=" * 60)

# Step 1: Load Embedding Model
logger.info("\n[1/5] Loading Sentence Transformer Embedding Model...")
try:
    from app.ai.embeddings.minilm_model import get_embedding_model
    start = time.time()
    model = get_embedding_model()
    elapsed = time.time() - start
    logger.success(f"✓ Embedding model loaded in {elapsed:.2f}s")
    logger.info(f"  Model: {model}")
except Exception as e:
    logger.error(f"✗ Failed to load embedding model: {e}")
    sys.exit(1)

# Step 2: Test Embedding Generation
logger.info("\n[2/5] Testing Embedding Generation...")
try:
    from app.ai.embeddings.minilm_model import generate_embedding
    test_text = "A thrilling action movie with amazing special effects"
    start = time.time()
    embedding = generate_embedding(test_text)
    elapsed = time.time() - start
    logger.success(f"✓ Generated embedding in {elapsed:.2f}s")
    logger.info(f"  Embedding dimension: {len(embedding)}")
except Exception as e:
    logger.error(f"✗ Failed to generate embedding: {e}")

# Step 3: Initialize Database Connection
logger.info("\n[3/5] Checking Database Connection...")
try:
    from app.db.session import SessionLocal
    db = SessionLocal()
    
    # Check if we have movies in database
    from app.models.movie import Movie
    movie_count = db.query(Movie).count()
    logger.info(f"  Movies in database: {movie_count}")
    
    if movie_count == 0:
        logger.warning("  ⚠ No movies found in database. FAISS index will be empty.")
        logger.warning("  ⚠ Please import the Netflix dataset first.")
    
    db.close()
    logger.success("✓ Database connection successful")
except Exception as e:
    logger.error(f"✗ Database connection failed: {e}")
    logger.warning("  Continuing without database-dependent features...")

# Step 4: Build FAISS Index
logger.info("\n[4/5] Building FAISS Index...")
try:
    from app.ai.faiss.build_index import FAISSIndexBuilder
    builder = FAISSIndexBuilder()
    
    start = time.time()
    success = builder.build_index()
    elapsed = time.time() - start
    
    if success:
        logger.success(f"✓ FAISS index built in {elapsed:.2f}s")
        logger.info(f"  Total vectors: {builder.index.ntotal if builder.index else 0}")
        logger.info(f"  Index saved to: {builder.index_path}")
    else:
        logger.warning("⚠ FAISS index build failed (likely no embeddings in database)")
        logger.warning("  The system will use fallback recommendations")
except Exception as e:
    logger.error(f"✗ Failed to build FAISS index: {e}")
    logger.warning("  The system will use fallback recommendations")

# Step 5: Initialize Recommendation Pipeline
logger.info("\n[5/5] Initializing Recommendation Pipeline...")
try:
    from app.ai.orchestration.recommendation_pipeline import get_pipeline
    start = time.time()
    pipeline = get_pipeline()
    elapsed = time.time() - start
    logger.success(f"✓ Recommendation pipeline initialized in {elapsed:.2f}s")
    logger.info(f"  Ranking profile: {pipeline.ranking_profile}")
    logger.info(f"  Diversity enabled: {pipeline.enable_diversity}")
    logger.info(f"  Cold start enabled: {pipeline.enable_cold_start}")
except Exception as e:
    logger.error(f"✗ Failed to initialize pipeline: {e}")

# Summary
logger.info("\n" + "=" * 60)
logger.info("AI Initialization Complete!")
logger.info("=" * 60)
logger.info("\nNext Steps:")
logger.info("1. If database is empty, import Netflix dataset:")
logger.info("   python -m app.db.import_netflix")
logger.info("\n2. Start the backend server:")
logger.info("   python -m uvicorn app.main:app --reload")
logger.info("\n3. Access API documentation:")
logger.info("   http://localhost:8000/docs")
logger.info("=" * 60)
