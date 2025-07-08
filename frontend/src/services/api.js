import axios from "axios";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Chat API
export const chatAPI = {
  sendMessage: async (message, sessionId = null) => {
    const response = await api.post("/chat", {
      message,
      session_id: sessionId,
    });
    return response.data;
  },
};

// Products API
export const productsAPI = {
  searchProducts: async (query) => {
    const response = await api.get("/products", {
      params: { query },
    });
    return response.data;
  },
};

// Outlets API
export const outletsAPI = {
  queryOutlets: async (query) => {
    const response = await api.get("/outlets", {
      params: { query },
    });
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get("/health");
    return response.data;
  },
};

export default api;
