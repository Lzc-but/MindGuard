import { defineStore } from "pinia";
import { getMe, login } from "../api/auth";
import { clearToken, getToken, setToken } from "../utils/token";

export type UserRole = "admin" | "user";

export interface UserInfo {
  username: string;
  role: UserRole;
}

interface LoginPayload {
  username: string;
  password: string;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: getToken(),
    user: null as UserInfo | null,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    isAdmin: (state) => state.user?.role === "admin",
  },
  actions: {
    async doLogin(payload: LoginPayload) {
      const res = await login(payload);
      this.token = res.access_token;
      setToken(res.access_token);
      await this.fetchMe();
    },
    async fetchMe() {
      const user = await getMe();
      this.user = user;
      return user;
    },
    logout() {
      this.token = "";
      this.user = null;
      clearToken();
    },
  },
});
