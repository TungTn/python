import axios, { AxiosError, type AxiosRequestConfig, type AxiosResponse } from "axios";
import { getToken } from "./auth";
import ApiService from "../services/servicesApi";
import eventBusService, { EVENT_BUS_ACTION } from "../services/eventBusService";

const mapError = (error: unknown): Error => {
  if (error instanceof AxiosError) {
    const message =
      (typeof error.response?.data === "string" && error.response.data) ||
      error.message ||
      "Request failed";
    return new Error(message);
  }
  if (error instanceof Error) {
    return error;
  }
  return new Error("Request failed");
};

async function request<T>(fn: () => Promise<AxiosResponse<T>>): Promise<AxiosResponse<T>> {
  try {
    return await fn();
  } catch (error) {
    throw mapError(error);
  }
}

export const apiPost = <T = unknown>(url: string, data: unknown) =>
  request<T>(() => ApiService.post<T>(url, data));

export const apiPatch = <T = unknown>(url: string, data: unknown) =>
  request<T>(() => ApiService.patch<T>(url, data));

export const apiGet = <T = unknown>(url: string, data?: Record<string, unknown>) =>
  request<T>(() => ApiService.get<T>(url, data));

export const apiGetCancel = <T = unknown>(url: string, signal?: AbortSignal) =>
  request<T>(() => ApiService.getCancel<T>(url, signal));

export const apiGetNoParam = <T = unknown>(url: string, config?: AxiosRequestConfig) =>
  request<T>(() => ApiService.getNoParam<T>(url, config));

export const apiGetFileNoParam = async (url: string): Promise<AxiosResponse<Blob>> => {
  try {
    const token = getToken();
    const client = axios.create({
      responseType: "blob",
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
    return await client.get<Blob>(url);
  } catch (error) {
    eventBusService.emit(EVENT_BUS_ACTION.SHOW_LOADING, false);
    throw mapError(error);
  }
};

export const apiPostNoParam = <T = unknown>(url: string) =>
  request<T>(() => ApiService.postNoParam<T>(url));

export const uploadFile = <T = unknown>(url: string, data: FormData | object) =>
  request<T>(() => ApiService.uploadFile<T>(url, data));

export const apiDelete = <T = unknown>(url: string) =>
  request<T>(() => ApiService.deleteNoParam<T>(url));
