export const DEFAULT_SYSTEM_PROMPT =
  process.env.NEXT_PUBLIC_DEFAULT_SYSTEM_PROMPT ||
  "";

export const API_HOST =
  // Use custom API endpoint
  (typeof process !== 'undefined' && process.env.API_HOST) || 'http://localhost:8000';

export const DEFAULT_TEMPERATURE = 
  parseFloat(process.env.NEXT_PUBLIC_DEFAULT_TEMPERATURE || "1");

// Timeout for API requests in milliseconds (default: 10 minutes)
export const API_TIMEOUT_DURATION = 
  parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || "600000");
