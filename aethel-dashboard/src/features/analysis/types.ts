export interface SimulationMetrics {
  expectedReturn?: number;
  var95?: number;
  worst5?: number;
  median?: number;
  best5?: number;
}

export interface TraceEntry {
  step: string;
  description: string;
}

export interface ChatMessage {
  role: 'user' | 'agent';
  content: string;
  sources?: string[];
}
