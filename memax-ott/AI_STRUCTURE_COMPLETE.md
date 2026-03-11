# AI Directory Structure - Complete ✅

## Overview
All required AI/ML files have been successfully added to the MEMAX OTT project.

## Complete AI Directory Structure

```
ai/
│
├── config.py ✅ [NEWLY ADDED]
├── __init__.py ✅
│
├── embeddings/
│   ├── __init__.py ✅
│   ├── minilm_model.py ✅
│   ├── text_preprocessor.py ✅ [NEWLY ADDED]
│   ├── build_movie_embeddings.py ✅
│   └── build_user_embeddings.py ✅
│
├── faiss/
│   ├── __init__.py ✅
│   ├── build_index.py ✅
│   ├── search.py ✅
│   └── index_store/
│       └── .gitkeep ✅
│       (memax_movie.index will be generated here)
│
├── ranking/
│   ├── __init__.py ✅
│   ├── hybrid_ranker.py ✅
│   ├── time_decay.py ✅
│   └── diversity.py ✅
│
├── cold_start/
│   ├── __init__.py ✅
│   ├── new_user.py ✅
│   └── new_movie.py ✅
│
├── baseline/
│   ├── __init__.py ✅
│   ├── popularity_model.py ✅
│   └── trending_model.py ✅
│
├── orchestration/
│   ├── __init__.py ✅
│   └── recommendation_pipeline.py ✅
│
└── evaluation/
    ├── __init__.py ✅
    └── metrics.py ✅
```

## Newly Added Files

### 1. `ai/config.py`
**Purpose**: Central configuration for all AI/ML components

**Features**:
- Embedding model configuration (MiniLM-L6-v2)
- FAISS index settings
- Ranking weights and parameters
- Time decay configuration
- Diversity settings
- Cold start thresholds
- Popularity and trending model settings
- Evaluation metrics configuration
- Batch processing settings
- Cache configuration
- Performance tuning

**Key Configuration Values**:
```python
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
TOP_K_CANDIDATES = 100
TOP_N_RECOMMENDATIONS = 20
EMBEDDING_WEIGHT = 0.6
POPULARITY_WEIGHT = 0.2
RECENCY_WEIGHT = 0.2
```

### 2. `ai/embeddings/text_preprocessor.py`
**Purpose**: Text cleaning and normalization for embeddings

**Features**:
- Unicode normalization
- Lowercase conversion
- Punctuation removal
- Number removal
- Extra space removal
- Text truncation
- HTML tag removal
- URL removal
- Special character removal
- Movie-specific text cleaning
- User-specific text cleaning

**Key Classes**:
```python
class TextPreprocessor:
    - preprocess(text: str) -> str
    - preprocess_batch(texts: List[str]) -> List[str]
    - clean_movie_text(title, description, genres) -> str
    - clean_user_text(preferences, history) -> str
```

## File Count Summary

| Directory      | Files | Status |
|---------------|-------|--------|
| ai/           | 2     | ✅     |
| embeddings/   | 5     | ✅     |
| faiss/        | 4     | ✅     |
| ranking/      | 4     | ✅     |
| cold_start/   | 3     | ✅     |
| baseline/     | 3     | ✅     |
| orchestration/| 2     | ✅     |
| evaluation/   | 2     | ✅     |
| **TOTAL**     | **25**| ✅     |

## Integration Points

### 1. Text Preprocessing
```python
from app.ai.embeddings.text_preprocessor import TextPreprocessor

preprocessor = TextPreprocessor()
clean_text = preprocessor.clean_movie_text(title, description, genres)
```

### 2. Configuration Usage
```python
from app.ai.config import AIConfig, EMBEDDING_DIM, TOP_N

# Access configuration
model_name = AIConfig.EMBEDDING_MODEL_NAME
index_path = AIConfig.get_index_path("movie")
```

### 3. Complete Pipeline
```python
from app.ai.orchestration.recommendation_pipeline import RecommendationPipeline
from app.ai.config import AIConfig

# Initialize pipeline with config
pipeline = RecommendationPipeline()
recommendations = await pipeline.get_recommendations(user_id, top_n=AIConfig.TOP_N_RECOMMENDATIONS)
```

## Next Steps

1. **Build Movie Embeddings**:
   ```bash
   python -m app.ai.embeddings.build_movie_embeddings
   ```

2. **Build FAISS Index**:
   ```bash
   python -m app.ai.faiss.build_index
   ```

3. **Test Recommendations**:
   ```bash
   python -m app.ai.orchestration.recommendation_pipeline
   ```

## Environment Variables

You can override configuration using environment variables:

```bash
AI_USE_GPU=true                    # Enable GPU for FAISS
AI_EMBEDDING_MODEL=custom-model    # Use custom embedding model
AI_TOP_N=30                        # Change number of recommendations
```

## Status: ✅ COMPLETE

All required AI/ML files are now in place and ready for use!

**Created**: 2026-02-06
**Last Updated**: 2026-02-06
