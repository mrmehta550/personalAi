const API_BASE_URL = '/api/v1';

export async function fetchSuggestions() {
  try {
    const res = await fetch(`${API_BASE_URL}/suggestions`);
    if (!res.ok) throw new Error('Failed to fetch suggestions');
    const data = await res.json();
    return data.suggestions || [];
  } catch (err) {
    console.error('Error fetching suggestions:', err);
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
  try {
    const res = await fetch(`${API_BASE_URL}/chat/history/${threadId}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.messages || [];
  } catch (err) {
    console.error('Error fetching history:', err);
    return [];
  }
}

export async function clearChatHistory(threadId) {
  try {
    const res = await fetch(`${API_BASE_URL}/chat/history/${threadId}`, {
      method: 'DELETE'
    });
    return res.ok;
  } catch (err) {
    console.error('Error clearing history:', err);
    return false;
  }
}

export async function fetchCollectionStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/kb/collections`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error('Error fetching KB stats:', err);
    return null;
  }
}
