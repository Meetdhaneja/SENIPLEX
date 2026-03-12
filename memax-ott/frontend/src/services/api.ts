import axios from 'axios';

const getBaseUrl = () => {
  if (typeof window === 'undefined') {
    // SSR / Server Side
    let url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      // If Render injected internal service name instead of full hostname
      url = url.includes('.') ? `https://${url}` : `https://${url}.onrender.com`;
    }
    return url.endsWith('/api') ? url : `${url}/api`;
  }
  
  // Client Browser: ALWAYS use relative proxy
  return '/api';
};

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
