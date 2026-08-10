import { useState, useRef, useCallback } from 'react';
import API_URL from '../config/api';

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamedText, setCurrentStreamedText] = useState('');
  const [activeMetadata, setActiveMetadata] = useState(null);

  const abortControllerRef = useRef(null);

  const streamMessage = useCallback(
    async ({ threadId, message, onComplete, onError }) => {
      setIsStreaming(true);
      setCurrentStreamedText('');
      setActiveMetadata(null);

      // Create a new AbortController for every request
      abortControllerRef.current = new AbortController();

      let accumulated = '';
      let metadataObj = null;

      try {
        if (!API_URL) {
          console.error('VITE_API_URL is missing. Failed request URL:', `${API_URL}/api/v1/chat/stream`);
          throw new Error(
            'VITE_API_URL is not configured. Please add it to Vercel Environment Variables.'
          );
        }

        const requestUrl = `${API_URL}/api/v1/chat/stream`;

        const response = await fetch(requestUrl, {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },

          body: JSON.stringify({
            thread_id: threadId,
            message: message,
            stream: true,
          }),

          signal: abortControllerRef.current.signal,
        });

        // Handle HTTP errors
        if (!response.ok) {
          let errorMessage = `HTTP error! status: ${response.status} at ${requestUrl}`;

          try {
            const errorData = await response.json();

            if (errorData?.detail) {
              errorMessage += ` - ${errorData.detail}`;
            }
          } catch {
            // Response was not JSON
          }

          console.error(`Failed streaming request: URL=${requestUrl}, Status=${response.status} ${response.statusText}`);
          throw new Error(errorMessage);
        }

        // Make sure streaming response exists
        if (!response.body) {
          throw new Error('Backend returned an empty response body.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        let buffer = '';

        while (true) {
          const { value, done } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, {
            stream: true,
          });

          // SSE events are separated by blank lines
          const events = buffer.split('\n\n');

          // Keep incomplete event for next chunk
          buffer = events.pop() || '';

          for (const event of events) {
            const lines = event.split('\n');

            for (const line of lines) {
              const trimmedLine = line.trim();

              // Ignore empty lines
              if (!trimmedLine) {
                continue;
              }

              // Ignore SSE comments
              if (trimmedLine.startsWith(':')) {
                continue;
              }

              // Only process data events
              if (!trimmedLine.startsWith('data:')) {
                continue;
              }

              const jsonString = trimmedLine
                .replace(/^data:\s*/, '')
                .trim();

              if (!jsonString) {
                continue;
              }

              try {
                const data = JSON.parse(jsonString);

                // -------------------------
                // METADATA EVENT
                // -------------------------
                if (data.event === 'metadata') {
                  metadataObj = data;

                  setActiveMetadata(data);
                }

                // -------------------------
                // TOKEN EVENT
                // -------------------------
                else if (data.event === 'token') {
                  if (typeof data.content === 'string') {
                    accumulated += data.content;

                    setCurrentStreamedText(accumulated);
                  }
                }

                // -------------------------
                // END EVENT
                // -------------------------
                else if (data.event === 'end') {
                  setIsStreaming(false);

                  if (onComplete) {
                    onComplete({
                      text: accumulated,
                      metadata: metadataObj || data,
                    });
                  }

                  return;
                }

                // -------------------------
                // ERROR EVENT
                // -------------------------
                else if (data.event === 'error') {
                  throw new Error(
                    data.message ||
                    data.error ||
                    'Backend streaming error'
                  );
                }
              } catch (parseError) {
                console.warn(
                  'Error parsing SSE event:',
                  jsonString,
                  parseError
                );
              }
            }
          }
        }

        // Stream finished without explicit "end" event
        setIsStreaming(false);

        if (onComplete) {
          onComplete({
            text: accumulated,
            metadata: metadataObj,
          });
        }
      } catch (error) {
        // User manually stopped the stream
        if (error?.name === 'AbortError') {
          console.log('Stream aborted by user.');
        } else {
          console.error('SSE Stream Error:', error);

          setIsStreaming(false);

          if (onError) {
            onError(error);
          }
        }

        setIsStreaming(false);
      } finally {
        abortControllerRef.current = null;
      }
    },
    []
  );

  // -------------------------
  // STOP STREAMING
  // -------------------------
  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();

      abortControllerRef.current = null;
    }

    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    currentStreamedText,
    activeMetadata,
    streamMessage,
    stopStreaming,
  };
}