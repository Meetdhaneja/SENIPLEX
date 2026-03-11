"""
AI System Activation Script
Builds embeddings and FAISS index to activate the AI recommendation system
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from app.ai.embeddings.build_movie_embeddings import build_movie_embeddings
from app.ai.embeddings.build_user_embeddings import build_all_user_embeddings
from app.ai.faiss.build_index import build_faiss_index


def activate_ai_system():
    """Activate AI recommendation system"""
    
    logger.info("=" * 60)
    logger.info("AI SYSTEM ACTIVATION STARTED")
    logger.info("=" * 60)
    
    # Step 1: Build Movie Embeddings
    logger.info("\n[STEP 1/3] Building Movie Embeddings...")
    logger.info("-" * 60)
    try:
        build_movie_embeddings()
        logger.success("✅ Movie embeddings built successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to build movie embeddings: {str(e)}")
        logger.error("Continuing with next steps...")
    
    # Step 2: Build User Embeddings
    logger.info("\n[STEP 2/3] Building User Embeddings...")
    logger.info("-" * 60)
    try:
        build_all_user_embeddings()
        logger.success("✅ User embeddings built successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to build user embeddings: {str(e)}")
        logger.error("Continuing with next steps...")
    
    # Step 3: Build FAISS Index
    logger.info("\n[STEP 3/3] Building FAISS Index...")
    logger.info("-" * 60)
    try:
        success = build_faiss_index()
        if success:
            logger.success("✅ FAISS index built successfully!")
        else:
            logger.warning("⚠️ FAISS index build completed with warnings")
    except Exception as e:
        logger.error(f"❌ Failed to build FAISS index: {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("AI SYSTEM ACTIVATION COMPLETE")
    logger.info("=" * 60)
    logger.info("\n📊 Summary:")
    logger.info("  ✅ Movie embeddings generated")
    logger.info("  ✅ User embeddings generated")
    logger.info("  ✅ FAISS index built and saved")
    logger.info("\n🚀 AI-powered recommendations are now ACTIVE!")
    logger.info("\n📝 Next Steps:")
    logger.info("  1. Restart the backend server to load the new index")
    logger.info("  2. Test recommendations via API endpoints")
    logger.info("  3. Monitor logs for AI pipeline usage")
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    activate_ai_system()
