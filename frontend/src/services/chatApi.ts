export interface ChatMessagePayload {
  sender: 'user' | 'bot';
  text: string;
  timestamp?: string;
}

export interface ChatRequestPayload {
  message: string;
  language?: string;
  conversation_history?: ChatMessagePayload[];
}

export interface ChatResponseData {
  response: string;
  intent: string;
  language: string;
}

export async function sendChatMessage(
  message: string,
  language: string = 'en',
  history: ChatMessagePayload[] = [],
  token?: string
): Promise<ChatResponseData> {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const endpoint = `${apiUrl}/chat`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };

  const authToken = token || localStorage.getItem('smart_agri_token');
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const payload: ChatRequestPayload = {
    message,
    language,
    conversation_history: history
  };

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      let errorMsg = 'Failed to get response from AI assistant.';
      try {
        const errData = await response.json();
        if (errData.detail) {
          errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
        }
      } catch {
        // ignore parse error
      }
      throw new Error(errorMsg);
    }

    return await response.json();
  } catch (err: unknown) {
    if (err instanceof TypeError && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
      throw new Error('The AI assistant is temporarily unavailable. Please check your internet connection and try again.');
    }
    if (err instanceof Error) {
      throw err;
    }
    throw new Error('Failed to get response from AI assistant.');
  }
}

