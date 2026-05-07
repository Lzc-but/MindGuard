import http from "./http";

export function uploadKnowledge(file: File): Promise<{ message: string; file: string }> {
  const form = new FormData();
  form.append("file", file);
  return http.post("/api/knowledge/upload", form);
}

export function rebuildKnowledgeIndex(): Promise<{ message: string; chunks: number }> {
  return http.post("/api/knowledge/rebuild");
}
