import http from "./http";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
}

export interface UserInfo {
  username: string;
  role: "admin" | "user";
}

export function login(payload: LoginPayload): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.append("username", payload.username);
  form.append("password", payload.password);
  return http.post("/api/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}

export function getMe(): Promise<UserInfo> {
  return http.get("/api/auth/me");
}
