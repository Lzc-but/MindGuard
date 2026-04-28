import http from "./http";

export interface MentalRequest {
  user_id: string;
  text: string;
}

export interface MentalResponse {
  status: "high_risk" | "medium_risk" | "low_risk";
  score: number;
  suggestion: string;
}

export function analyzeMental(payload: MentalRequest): Promise<MentalResponse> {
  return http.post("/api/mental/analyze", payload);
}
