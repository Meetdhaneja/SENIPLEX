import api from "./api";

export const movieService = {
  async getMovies(page = 1, pageSize = 20, contentType?: string) {
    const response = await api.get("movies", { // Removed leading slash
      params: { page, page_size: pageSize, content_type: contentType },
    });
    return response.data;
  },

  async getMovie(id: number) {
    const response = await api.get(`movies/${id}`); // Removed leading slash
    return response.data;
  },

  async getFeaturedMovies(limit = 10) {
    const response = await api.get("movies/featured", { // Removed leading slash
      params: { limit },
    });
    return response.data;
  },

  async getTrendingMovies(limit = 10) {
    const response = await api.get("movies/trending", { // Removed leading slash
      params: { limit },
    });
    return response.data;
  },

  async searchMovies(query: string, limit = 20) {
    const response = await api.get("movies/search", { // Removed leading slash
      params: { q: query, limit },
    });
    return response.data;
  },
};
