import { DEFAULT_SYSTEM_PROMPT, DEFAULT_TEMPERATURE } from '@/utils/app/const';
import { ApiError, ApiStream } from '@/utils/server';

import { ChatBody, Message } from '@/types/chat';


export const config = {
  runtime: 'edge',
};

const handler = async (req: Request): Promise<Response> => {
  try {
    const { model, system, options, messages } = (await req.json()) as ChatBody;


    let promptToSend = system;
    if (!promptToSend) {
      promptToSend = DEFAULT_SYSTEM_PROMPT;
    }

    let temperatureToUse = options?.temperature;
    if (temperatureToUse == null) {
      temperatureToUse = DEFAULT_TEMPERATURE;
    }

    const stream = await ApiStream(model || '', promptToSend, temperatureToUse, messages);

    return new Response(stream);
  } catch (error) {
    console.error('Chat API error:', error);
    if (error instanceof ApiError) {
      // Return a more descriptive error message to help with debugging
      return new Response(JSON.stringify({ 
        error: 'API Error', 
        message: error.message,
        suggestion: 'Check if the API endpoint is running and accessible'
      }), { 
        status: 500, 
        headers: {
          'Content-Type': 'application/json'
        } 
      });
    } else {
      return new Response(JSON.stringify({ 
        error: 'Internal Server Error', 
        message: error instanceof Error ? error.message : 'Unknown error'
      }), { 
        status: 500,
        headers: {
          'Content-Type': 'application/json'
        } 
      });
    }
  }
};

export default handler;
