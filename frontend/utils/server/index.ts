import { Message } from '@/types/chat';
import { OllamaModel } from '@/types/ollama';

import { API_HOST, API_TIMEOUT_DURATION } from '../app/const';

import {
  ParsedEvent,
  ReconnectInterval,
  createParser,
} from 'eventsource-parser';

export class ApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const ApiStream = async (
  model: string,
  systemPrompt: string,
  temperature: number,
  messages: Message[],
) => {
  let url = `${API_HOST}/llm`;
  
  // Create an AbortController with a long timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_DURATION);
  
  try {
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
      },
      method: 'POST',
      body: JSON.stringify({
        messages: messages,
      }),
      signal: controller.signal,
    });
    
    // Clear the timeout since the request has completed
    clearTimeout(timeoutId);

    if (res.status !== 200) {
      let errorMessage = `API returned status ${res.status}`;
      try {
        const result = await res.json();
        if (result.error) {
          errorMessage = result.error;
        }
      } catch (e) {
        // If we can't parse the error response, use the status code
      }
      throw new ApiError(errorMessage);
    }

    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    // Check if the response is streaming (has a readable stream)
    if (res.body) {
      const responseStream = new ReadableStream({
        async start(controller) {
          try {
            const reader = res.body!.getReader();
            
            while (true) {
              const { done, value } = await reader.read();
              
              if (done) {
                controller.close();
                break;
              }
              
              const text = decoder.decode(value, { stream: true });
              
              // Try to parse as JSON for structured responses
              try {
                const lines = text.split('\n').filter(line => line.trim());
                for (const line of lines) {
                  if (line.trim()) {
                    try {
                      const parsedData = JSON.parse(line);
                      // Handle different response formats
                      if (parsedData.response) {
                        controller.enqueue(encoder.encode(parsedData.response));
                      } else if (parsedData.content) {
                        controller.enqueue(encoder.encode(parsedData.content));
                      } else if (parsedData.text) {
                        controller.enqueue(encoder.encode(parsedData.text));
                      } else if (typeof parsedData === 'string') {
                        controller.enqueue(encoder.encode(parsedData));
                      }
                    } catch (jsonError) {
                      // If it's not JSON, treat as plain text
                      controller.enqueue(encoder.encode(line));
                    }
                  }
                }
              } catch (parseError) {
                // If parsing fails, stream the raw text
                controller.enqueue(value);
              }
            }
          } catch (e) {
            controller.error(e);
          }
        },
      });
      
      return responseStream;
    } else {
      // Handle non-streaming response
      const result = await res.json();
      let responseText = '';
      
      if (result.response) {
        responseText = result.response;
      } else if (result.content) {
        responseText = result.content;
      } else if (result.text) {
        responseText = result.text;
      } else if (typeof result === 'string') {
        responseText = result;
      } else {
        responseText = JSON.stringify(result);
      }
      
      const responseStream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(responseText));
          controller.close();
        },
      });
      
      return responseStream;
    }
  } catch (error) {
    // Clear the timeout if there was an error
    clearTimeout(timeoutId);
    
    // Check if this is a connection error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError(
        `Connection error: Could not connect to API at ${API_HOST}/llm. Please ensure the API endpoint is accessible and running.`
      );
    }
    
    // Re-throw other errors
    throw error;
  }
};
