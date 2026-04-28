import axios from "axios";
import { ElMessage } from "element-plus";
import { clearToken, getToken } from "../utils/token";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/",
  timeout: 15000,
});

http.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error?.response?.status;
    const detail = error?.response?.data?.detail || "请求失败";

    if (status === 401) {
      clearToken();
      ElMessage.error("登录状态已失效，请重新登录");
      window.location.href = "/login";
    } else if (status === 403) {
      ElMessage.error("无权限访问该功能");
    } else {
      ElMessage.error(String(detail));
    }

    return Promise.reject(error);
  },
);

export default http;
