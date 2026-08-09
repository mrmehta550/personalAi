import { useState, useRef, useCallback } from 'react';

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamedText, setCurrentStreamedText] = useState('');
  const [activeMetadata, setActiveMetadata] = useState(null);
  const abortControllerRef = useRef(null);

  const streamMessage = useCallback(async ({ threadId, message, onComplete, onError }) => {
    setIsStreaming(true);
    setCurrentStreamedText('');
    setActiveMetadata(null);

    abortControllerRef.current = new AbortController();
    let accumulated = '';
    let metadataObj = null;

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          message: message,
          stream: true
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep incomplete trailing line in buffer

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data: ')) continue;

          const jsonStr = trimmed.replace('data: ', '');
          try {
            const data = JSON.parse(jsonStr);

            if (data.event === 'metadata') {
              metadataObj = data;
              setActiveMetadata(data);
            } else if (data.event === 'token') {
              accumulated += data.content;
              setCurrentStreamedText(accumulated);
            } else if (data.event === 'end') {
              setIsStreaming(false);
              if (onComplete) {
                onComplete({
                  text: accumulated,
                  metadata: metadataObj || data
                });
              }
              return;
            }
          } catch (e) {
            console.warn('Error parsing SSE data event line:', jsonStr, e);
          }
        }
      }

      setIsStreaming(false);
      if (onComplete) {
        onComplete({ text: accumulated, metadata: metadataObj });
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Stream aborted by user');
      } else {
        console.error('SSE Stream Error:', err);
        if (onError) onError(err);
      }
      setIsStreaming(false);
    }
  }, []);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  return {
    isStreaming,
    currentStreamedText,
    activeMetadata,
    streamMessage,
    stopStreaming
  };
}
