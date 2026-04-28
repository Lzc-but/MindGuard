import http from "./http";

export interface ChatResponse {
  answer: string;
  references: string[];
}

export interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export function listConversations(): Promise<ConversationItem[]> {
  return http.get("/api/chat/conversations");
}

export function createConversation(title?: string): Promise<ConversationItem> {
  return http.post("/api/chat/conversations", { title });
}

export function deleteConversation(conversationId: string): Promise<{ message: string }> {
  return http.delete(`/api/chat/conversations/${conversationId}`);
}

export function renameConversation(conversationId: string, title: string): Promise<ConversationItem> {
  return http.patch(`/api/chat/conversations/${conversationId}`, { title });
}

export function listConversationMessages(conversationId: string): Promise<ConversationMessage[]> {
  return http.get(`/api/chat/conversations/${conversationId}/messages`);
}

export function sendConversationMessage(conversationId: string, question: string): Promise<ChatResponse> {
  return http.post(`/api/chat/conversations/${conversationId}/messages`, { question });
}
