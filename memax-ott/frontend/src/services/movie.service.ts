import api from "./api";

export const movieService = {
  async getMovies(page = 1, pageSize = 20, contentType?: string) {
    const response = await api.get("/movies/", {
      params: { page, page_size: pageSize, content_type: contentType },
    });
    return response.data;
  },

  async getMovie(id: number) {
    const response = await api.get(`/movies/${id}/`);
    return response.data;
  },

  async getFeaturedMovies(limit = 10) {
    const response = await api.get("/movies/featured/", {
      params: { limit },
    });
    return response.data;
  },

  async getTrendingMovies(limit = 10) {
    const response = await api.get("/movies/trending/", {
      params: { limit },
    });
    return response.data;
  },

  async searchMovies(query: string, limit = 20) {
    const response = await api.get("/movies/search/", {
      params: { q: query, limit },
    });
    return response.data;
  },
};
