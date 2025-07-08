import { API_HOST } from '@/utils/app/const';
import { OllamaModelDetail } from '@/types/ollama';

export const config = {
  runtime: 'edge',
};

const handler = async (req: Request): Promise<Response> => {
  try {
    const { name } = await req.json();

    if (typeof name !== 'string' || name.trim() === '') {
      return new Response('Name parameter is required', { status: 400 });
    }

    // Since we're using a custom API endpoint, return default model details
    const modelDetail: OllamaModelDetail = {
      modelfile: 'Custom LLM Model',
      parameters: 'Custom parameters',
      template: 'Custom template',
      details: {
        format: 'custom',
        family: 'custom',
        families: ['custom'],
        parameter_size: '0B',
        quantization_level: 'custom'
      }
    };

    return new Response(JSON.stringify(modelDetail), { status: 200 });
  } catch (error) {
    console.error('Model details API error:', error);
    
    return new Response(JSON.stringify({
      error: 'Error fetching model details',
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
