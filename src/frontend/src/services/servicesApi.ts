import axios, { type AxiosRequestConfig, type AxiosResponse } from "axios";
import { API_BASE_URL } from "../api/api";
import { getToken } from "../api/auth";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const service = {
  init() {
    return;
  },

  getNoToken<T = unknown>(url: string) {
    return axios.get<T>(url);
  },

  get<T = unknown>(url: string, params?: Record<string, unknown>) {
    return client.get<T>(url, { params });
  },

  getCancel<T = unknown>(url: string, signal?: AbortSignal) {
    return client.get<T>(url, { signal });
  },

  post<T = unknown>(url: string, params?: unknown) {
    return client.post<T>(url, params);
  },

  patch<T = unknown>(url: string, params?: unknown) {
    return client.patch<T>(url, params);
  },

  getNoParam<T = unknown>(url: string, config?: AxiosRequestConfig) {
    return client.get<T>(url, config);
  },

  getFileNoParam(url: string) {
    return client.get(url, { responseType: "blob" });
  },

  postNoParam<T = unknown>(url: string) {
    return client.post<T>(url);
  },

  uploadFile<T = unknown>(url: string, params: FormData | object) {
    return client.post<T>(url, params, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  deleteNoParam<T = unknown>(url: string): Promise<AxiosResponse<T>> {
    return client.delete<T>(url);
  },
};

export default service;
