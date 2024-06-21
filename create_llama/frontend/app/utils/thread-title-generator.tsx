import { useContext, useState } from 'react';
import ChatContext from '../context/chat-context';

export function useGenerateTitle() {
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatContext = useContext(ChatContext);

  const generateTitle = async (question: string) => {
    setLoading(true);
    setError(null);
    try {
      const access_token = localStorage.getItem("access_token");
      const response = await fetch(`/api/chat?question=${encodeURIComponent(question)}`, {
        method: "GET",
        headers:{
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${access_token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch title');
      }

      const jsonResponse = await response.json();

      const finalResponse = `${jsonResponse.title.replaceAll("\"", "")}...`;

      setTitle(finalResponse);

      chatContext && chatContext.selectedThread && chatContext.setSelectedThread({...chatContext.selectedThread, title: finalResponse})
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { title, loading, error, generateTitle };
}
