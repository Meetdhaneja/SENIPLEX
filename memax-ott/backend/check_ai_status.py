"""
AI Activation Status Check
Checks if AI components are ready and provides activation instructions
"""
from pathlib import Path
from loguru import logger


def check_ai_status():
    """Check AI system status"""
    
    logger.info("=" * 70)
    logger.info("AI SYSTEM STATUS CHECK")
    logger.info("=" * 70)
    
    # Check 1: FAISS Index
    logger.info("\n[CHECK 1] FAISS Index")
    logger.info("-" * 70)
    
    index_paths = [
        Path("app/ai/faiss/index_store/memax_movie.index"),
        Path("backend/app/ai/faiss/index_store/memax_movie.index"),
    ]
    
    index_found = False
    for index_path in index_paths:
        if index_path.exists():
            logger.success(f"✅ FAISS index found: {index_path}")
            logger.info(f"   Size: {index_path.stat().st_size / 1024:.2f} KB")
            index_found = True
            break
    
    if not index_found:
        logger.warning("⚠️  FAISS index not found")
        logger.info("   Expected location: app/ai/faiss/index_store/memax_movie.index")
    
    # Check 2: Model Cache
    logger.info("\n[CHECK 2] Embedding Model")
    logger.info("-" * 70)
    
    model_cache_paths = [
        Path("app/ai/model_cache"),
        Path("backend/app/ai/model_cache"),
        Path.home() / ".cache" / "huggingface" / "hub"
    ]
    
    model_found = False
    for cache_path in model_cache_paths:
        if cache_path.exists():
            logger.success(f"✅ Model cache directory found: {cache_path}")
            model_found = True
            break
    
    if not model_found:
        logger.warning("⚠️  Model cache not found (will download on first use)")
    
    # Check 3: Configuration
    logger.info("\n[CHECK 3] AI Configuration")
    logger.info("-" * 70)
    
    try:
        from app.ai.config import AIConfig
        logger.success("✅ AI configuration loaded")
        logger.info(f"   Model: {AIConfig.EMBEDDING_MODEL_NAME}")
        logger.info(f"   Embedding Dimension: {AIConfig.EMBEDDING_DIMENSION}")
        logger.info(f"   Top N Recommendations: {AIConfig.TOP_N_RECOMMENDATIONS}")
    except Exception as e:
        logger.error(f"❌ Failed to load AI config: {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("ACTIVATION INSTRUCTIONS")
    logger.info("=" * 70)
    
    if not index_found:
        logger.info("\n🔧 To activate AI recommendations:")
        logger.info("\n   Option 1: Run the activation script")
        logger.info("   ```")
        logger.info("   cd backend")
        logger.info("   python activate_ai.py")
        logger.info("   ```")
        logger.info("\n   Option 2: Build components individually")
        logger.info("   ```")
        logger.info("   cd backend")
        logger.info("   python -m app.ai.embeddings.build_movie_embeddings")
        logger.info("   python -m app.ai.embeddings.build_user_embeddings")
        logger.info("   python -m app.ai.faiss.build_index")
        logger.info("   ```")
        logger.info("\n   Note: Ensure the database has movie data before building embeddings")
    else:
        logger.success("\n✅ AI system appears to be activated!")
        logger.info("\n   The recommendation service will use AI-powered recommendations.")
        logger.info("   Restart the backend server to ensure the index is loaded.")
    
    logger.info("\n" + "=" * 70)


if __name__ == "__main__":
    check_ai_status()
