# AI System Activation Guide 🚀

## Current Status: ⚠️ PENDING ACTIVATION

The AI recommendation pipeline has been **integrated** but needs to be **activated** by building the necessary components.

## Prerequisites ✅

Before activating the AI system, ensure:

1. **Database is running** and accessible
2. **Movie data is loaded** into the database
3. **Backend dependencies are installed** (sentence-transformers, faiss-cpu, etc.)

## Activation Steps

### Quick Activation (Recommended)

Run the automated activation script:

```bash
cd backend
python activate_ai.py
```

This will:
1. Build movie embeddings (generates vector representations for all movies)
2. Build user embeddings (generates vector representations based on user interactions)
3. Build FAISS index (creates fast similarity search index)

### Manual Activation (Step-by-Step)

If you prefer to run each step individually:

#### Step 1: Build Movie Embeddings

```bash
cd backend
python -m app.ai.embeddings.build_movie_embeddings
```

**What it does:**
- Fetches all movies from database
- Generates 384-dimensional embeddings using MiniLM-L6-v2
- Combines title, description, and genres into text
- Stores embeddings in `movie_embeddings` table

**Expected output:**
```
Building embeddings for X movies
Movie embeddings built successfully
```

#### Step 2: Build User Embeddings

```bash
cd backend
python -m app.ai.embeddings.build_user_embeddings
```

**What it does:**
- Fetches all users with interactions
- Calculates weighted average of watched movie embeddings
- Stores user preference vectors in `user_embeddings` table

**Expected output:**
```
Building embeddings for X users
User embeddings built successfully
```

#### Step 3: Build FAISS Index

```bash
cd backend
python -m app.ai.faiss.build_index
```

**What it does:**
- Loads all movie embeddings from database
- Creates FAISS IndexFlatIP (cosine similarity)
- Normalizes vectors for efficient search
- Saves index to `app/ai/faiss/index_store/memax_movie.index`

**Expected output:**
```
Building FAISS index...
Loaded X embeddings with dimension 384
FAISS index built with X vectors
FAISS index saved to app/ai/faiss/index_store/memax_movie.index
```

## Verification

### Check AI Status

```bash
cd backend
python check_ai_status.py
```

This will show:
- ✅ FAISS index status
- ✅ Model cache status
- ✅ Configuration status

### Test Recommendations

After activation, test the AI recommendations:

```bash
# Start the backend server
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, test the API
curl -X POST "http://localhost:8000/api/v1/recommendations/personalized" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 20, "exclude_watched": true}'
```

## Troubleshooting

### Issue: "No embeddings found in database"

**Cause:** No movies in the database

**Solution:**
1. Import movie data first
2. Run the dataset import script:
   ```bash
   cd memax-ott
   .\IMPORT_DATA.bat
   ```

### Issue: "Database connection error"

**Cause:** Database not running or incorrect credentials

**Solution:**
1. Check database is running
2. Verify connection string in `app/core/config.py`
3. Test connection:
   ```bash
   python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('Connected!'); db.close()"
   ```

### Issue: "Model download taking too long"

**Cause:** First-time download of MiniLM-L6-v2 model (~90MB)

**Solution:**
- Be patient, it only downloads once
- Model is cached in `~/.cache/huggingface/`
- Subsequent runs will be fast

### Issue: "Out of memory"

**Cause:** Too many embeddings for available RAM

**Solution:**
1. Process in batches (modify `EMBEDDING_BATCH_SIZE` in `ai/config.py`)
2. Use smaller model (modify `EMBEDDING_MODEL_NAME`)
3. Increase system RAM

## Configuration

Customize AI behavior in `backend/app/ai/config.py`:

```python
# Recommendation settings
AIConfig.TOP_N_RECOMMENDATIONS = 20
AIConfig.TOP_K_CANDIDATES = 100

# Ranking weights
AIConfig.EMBEDDING_WEIGHT = 0.6
AIConfig.POPULARITY_WEIGHT = 0.2
AIConfig.RECENCY_WEIGHT = 0.2

# Diversity
AIConfig.DIVERSITY_LAMBDA = 0.5
AIConfig.MIN_GENRE_DIVERSITY = 0.3

# Cold start
AIConfig.NEW_USER_THRESHOLD_DAYS = 7
AIConfig.MIN_USER_INTERACTIONS = 5
```

## Maintenance

### Rebuild Index (After Adding New Movies)

```bash
cd backend
python -m app.ai.faiss.build_index
```

### Update User Embeddings (After New Interactions)

```bash
cd backend
python -m app.ai.embeddings.build_user_embeddings
```

### Schedule Regular Updates

For production, schedule these tasks:

```bash
# Daily: Rebuild FAISS index
0 2 * * * cd /path/to/backend && python -m app.ai.faiss.build_index

# Every 6 hours: Update user embeddings
0 */6 * * * cd /path/to/backend && python -m app.ai.embeddings.build_user_embeddings
```

## Performance Expectations

### Build Times (Approximate)

| Component | 1K Movies | 10K Movies | 100K Movies |
|-----------|-----------|------------|-------------|
| Movie Embeddings | ~30s | ~5min | ~50min |
| User Embeddings | ~10s | ~1min | ~10min |
| FAISS Index | ~1s | ~5s | ~30s |

### Recommendation Speed

- **FAISS Search**: < 10ms for 100K movies
- **Hybrid Ranking**: < 50ms
- **Total Response**: < 100ms

## What Happens Without Activation?

If you don't activate the AI system:

- ✅ **Backend still works** - No errors or crashes
- ✅ **Recommendations still provided** - Uses fallback logic
- ⚠️ **Fallback mode** - Simple rating-based recommendations
- ⚠️ **No personalization** - Same recommendations for all users
- ⚠️ **No similarity search** - Genre-based similar movies only

The system gracefully degrades to simple logic until AI is activated.

## Activation Checklist

- [ ] Database is running
- [ ] Movie data is imported
- [ ] Dependencies are installed
- [ ] Run `python activate_ai.py`
- [ ] Verify with `python check_ai_status.py`
- [ ] Restart backend server
- [ ] Test recommendations via API
- [ ] Monitor logs for "AI recommendations" messages

## Next Steps After Activation

1. **Monitor Performance**
   - Check logs for AI pipeline usage
   - Track recommendation response times
   - Monitor FAISS index size

2. **A/B Testing**
   - Compare AI vs fallback recommendations
   - Measure click-through rates
   - Analyze user engagement

3. **Optimize**
   - Adjust ranking weights based on metrics
   - Fine-tune diversity parameters
   - Experiment with different models

## Support

For issues or questions:
- Check logs in `backend/logs/`
- Review error messages carefully
- Ensure all prerequisites are met
- Verify database has movie data

---

**Status**: Ready for activation ✅  
**Last Updated**: 2026-02-06  
**Integration**: Complete ✅  
**Activation**: Pending ⏳
