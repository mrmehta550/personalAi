import { useState, useEffect } from 'react';
import { fetchSuggestions } from '../services/api';

export function useSuggestions() {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchSuggestions().then(data => {
      if (mounted) {
        setSuggestions(data);
        setLoading(false);
      }
    });
    return () => { mounted = false; };
  }, []);

  return { suggestions, loading };
}
