import API_URL from '../config/api';

export async function fetchSuggestions() {
  const url = `${API_URL}/api/v1/suggestions`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.error(`Failed request: URL=${url}, Status=${res.status} ${res.statusText}`);
      throw new Error(`Failed to fetch suggestions: HTTP status ${res.status}`);
    }
    const data = await res.json();
    return data.suggestions || [];
  } catch (err) {
    console.error(`Error fetching suggestions from ${url}:`, err);
    return [
      "Tell me about your projects",
      "Tell me about your AI Mail Automation project",
      "What technologies do you use?",
      "What are your strongest technical skills?",
      "Tell me about your AI experience",
      "Explain your Personal AI Assistant",
      "How can I contact you?"
    ];
  }
}

export async function fetchChatHistory(threadId) {
  const url = `${API_URL}/api/v1/chat/history/${threadId}`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.error(`Failed request: URL=${url}, Status=${res.status} ${res.statusText}`);
      return [];
    }
    const data = await res.json();
    return data.messages || [];
  } catch (err) {
    console.error(`Error fetching history from ${url}:`, err);
    return [];
  }
}

export async function clearChatHistory(threadId) {
  const url = `${API_URL}/api/v1/chat/history/${threadId}`;
  try {
    const res = await fetch(url, {
      method: 'DELETE'
    });
    if (!res.ok) {
      console.error(`Failed request: URL=${url}, Status=${res.status} ${res.statusText}`);
      return false;
    }
    return res.ok;
  } catch (err) {
    console.error(`Error clearing history from ${url}:`, err);
    return false;
  }
}

export async function fetchCollectionStats() {
  const url = `${API_URL}/api/v1/kb/collections`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.error(`Failed request: URL=${url}, Status=${res.status} ${res.statusText}`);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error(`Error fetching KB stats from ${url}:`, err);
    return null;
  }
}
