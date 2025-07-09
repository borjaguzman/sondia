import { API_HOST } from '@/utils/app/const';

import { OllamaModel, OllamaModelID, OllamaModels } from '@/types/ollama';

export const config = {
  runtime: 'edge',
};

const handler = async (req: Request): Promise<Response> => {
  try {
    // Since we're using a custom API endpoint, we'll return a default model
    // You can modify this to match the models available in your API
    const models: OllamaModel[] = [
      {
        id: 'default',
        name: 'Custom LLM Model',
        modified_at: new Date().toISOString(),
        size: 0,
      }
    ];

    return new Response(JSON.stringify(models), { status: 200 });
  } catch (error) {
    console.error('Models API error:', error);
    
    return new Response(JSON.stringify({
      error: 'Error fetching models',
      message: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};

export default handler;
