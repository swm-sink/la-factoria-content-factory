import { useState } from 'react';
import { useApiKeyStore } from '../store/useApiKeyStore';

export const ApiKeyManager = () => {
  const { apiKey, setApiKey } = useApiKeyStore();
  const [input, setInput] = useState(apiKey);
  const [status, setStatus] = useState<'idle' | 'saved' | 'error'>('idle');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input || input.length < 10) {
      setStatus('error');
      return;
    }
    setApiKey(input);
    setStatus('saved');
    setTimeout(() => setStatus('idle'), 2000);
  };

  return (
    <form onSubmit={handleSave} className="flex items-center space-x-2">
      <input
        type="password"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter API Key"
        className="border rounded px-2 py-1 text-sm"
        minLength={10}
        required
      />
      <button
        type="submit"
        className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
      >
        Save
      </button>
      {status === 'saved' && <span className="text-green-600 text-xs ml-2">Saved!</span>}
      {status === 'error' && <span className="text-red-600 text-xs ml-2">Invalid key</span>}
      {apiKey && status === 'idle' && <span className="text-green-500 text-xs ml-2">Key set</span>}
    </form>
  );
}; 