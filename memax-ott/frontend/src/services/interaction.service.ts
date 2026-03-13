import api from "./api";

export const interactionService = {
    async likeMovie(movieId: number) {
        const response = await api.post(`likes`, null, {
            params: { movie_id: movieId }
        });
        return response.data;
    },

    async unlikeMovie(movieId: number) {
        const response = await api.delete(`likes/${movieId}`);
        return response.data;
    },

    async addToWatchLater(movieId: number) {
        const response = await api.post("interactions", {
            movie_id: movieId,
            interaction_type: "watch_later",
            interaction_value: 1.0,
        });
        return response.data;
    },

    async dislikeMovie(movieId: number) {
        const response = await api.post("interactions", {
            movie_id: movieId,
            interaction_type: "dislike",
            interaction_value: 1.0,
        });
        return response.data;
    },

    async getMyLikes() {
        const response = await api.get("likes");
        return response.data;
    },

    async recordView(movieId: number) {
        const response = await api.post("interactions", {
            movie_id: movieId,
            interaction_type: "view",
            interaction_value: 1.0
        });
        return response.data;
    },

    async recordSearchClick(movieId: number) {
        const response = await api.post("interactions", {
            movie_id: movieId,
            interaction_type: "search_click",
            interaction_value: 1.2
        });
        return response.data;
    },

    /**
     * Record watch progress.
     * percentWatched: 0.0 - 1.0 (e.g. 0.3 = watched 30% then skipped)
     * Lower values signal a skip; higher values signal engagement.
     */
    async recordWatchProgress(movieId: number, percentWatched: number) {
        const interactionValue = Math.min(1.5, Math.max(0.1, percentWatched * 1.5));
        const interactionType =
            percentWatched < 0.3
                ? "skip"
                : percentWatched >= 0.9
                ? "complete"
                : "partial_view";
        const response = await api.post("interactions", {
            movie_id: movieId,
            interaction_type: interactionType,
            interaction_value: interactionValue,
        });
        return response.data;
    },
};
