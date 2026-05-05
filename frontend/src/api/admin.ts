import http from "./http";

export interface UserItem {
  id: string;
  username: string;
  role: string;
  display_name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CreateUserPayload {
  username: string;
  password: string;
  role: string;
  display_name: string;
}

export interface UpdateUserPayload {
  role?: string;
  display_name?: string;
  status?: string;
  password?: string;
}

export const listUsers = (): Promise<UserItem[]> =>
  http.get("/api/admin/users");

export const createUser = (payload: CreateUserPayload): Promise<UserItem> =>
  http.post("/api/admin/users", payload);

export const updateUser = (id: string, payload: UpdateUserPayload): Promise<UserItem> =>
  http.patch(`/api/admin/users/${id}`, payload);

export const deleteUser = (id: string): Promise<void> =>
  http.delete(`/api/admin/users/${id}`);