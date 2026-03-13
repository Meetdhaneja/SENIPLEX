import api from "./api";

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export const authService = {
  async login(data: LoginData) {
    const formData = new FormData();
    formData.append("username", data.email);
    formData.append("password", data.password);

    // URL relative to baseURL (http://localhost:8000/api)
    const response = await api.post("auth/login", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
    }

    return response.data;
  },

  async signup(data: SignupData) {
    const response = await api.post("auth/signup", data);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get("auth/me");
    return response.data;
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};
