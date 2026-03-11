-- Database Indexes for Performance

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Movies indexes
CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
CREATE INDEX IF NOT EXISTS idx_movies_content_type ON movies(content_type);
CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies(rating DESC);
CREATE INDEX IF NOT EXISTS idx_movies_view_count ON movies(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_movies_is_featured ON movies(is_featured);
CREATE INDEX IF NOT EXISTS idx_movies_release_year ON movies(release_year DESC);

-- Watch history indexes
CREATE INDEX IF NOT EXISTS idx_watch_history_user_id ON watch_history(user_id);
CREATE INDEX IF NOT EXISTS idx_watch_history_movie_id ON watch_history(movie_id);
CREATE INDEX IF NOT EXISTS idx_watch_history_watched_at ON watch_history(watched_at DESC);
CREATE INDEX IF NOT EXISTS idx_watch_history_user_movie ON watch_history(user_id, movie_id);

-- Watch progress indexes
CREATE INDEX IF NOT EXISTS idx_watch_progress_user_id ON watch_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_watch_progress_movie_id ON watch_progress(movie_id);
CREATE INDEX IF NOT EXISTS idx_watch_progress_last_watched ON watch_progress(last_watched_at DESC);

-- Interactions indexes
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_movie_id ON interactions(movie_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_interactions_user_movie ON interactions(user_id, movie_id);

-- User features indexes
CREATE INDEX IF NOT EXISTS idx_user_features_user_id ON user_features(user_id);

-- Movie embeddings indexes
CREATE INDEX IF NOT EXISTS idx_movie_embeddings_movie_id ON movie_embeddings(movie_id);
CREATE INDEX IF NOT EXISTS idx_movie_embeddings_faiss_id ON movie_embeddings(faiss_index_id);

-- Recommendation logs indexes
CREATE INDEX IF NOT EXISTS idx_recommendation_logs_user_id ON recommendation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_logs_movie_id ON recommendation_logs(movie_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_logs_timestamp ON recommendation_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_recommendation_logs_type ON recommendation_logs(recommendation_type);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_movies_rating_views ON movies(rating DESC, view_count DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_user_type_time ON interactions(user_id, interaction_type, timestamp DESC);
