from app.ai.baseline import popularity_model


async def generate_recommendations(user_id, db):
    """
    Orchestrates:
    embeddings -> faiss -> ranking -> cold start
    """

    # placeholder safe pipeline
    model = popularity_model.PopularityModel()
    popular = model.get_popular_movies(db=db, count=20)
    ranked = sorted(popular, key=lambda x: x[1], reverse=True)
    return [movie_id for movie_id, _score in ranked[:10]]
