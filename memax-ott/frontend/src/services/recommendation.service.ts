import api from "./api";

export const recommendationService = {
  async getPersonalizedRecommendations(limit = 20) {
    const response = await api.post("recommendations/personalized", {
      limit,
      exclude_watched: true,
    });
    return response.data;
  },

  async getSimilarMovies(movieId: number, limit = 10) {
    const response = await api.get(`recommendations/similar/${movieId}`, {
      params: { limit },
    });
    return response.data;
  },

  async getColdStartRecommendations(limit = 20) {
    const response = await api.get("recommendations/cold-start", {
      params: { limit },
    });
    return response.data;
  },
};

