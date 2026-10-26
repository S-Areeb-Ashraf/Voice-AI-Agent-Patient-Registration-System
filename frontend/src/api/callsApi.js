import { apiUrl } from './config';

// Backend origin comes from VITE_API_BASE_URL (see config.js) — nothing hardcoded.

async function handleResponse(response) {
  let json;
  try {
    json = await response.json();
  } catch (err) {
    throw new Error(`Failed to parse server response: ${response.statusText}`);
  }

  // Handle envelope shape { data: ..., error: ... }
  if (json && json.hasOwnProperty('error') && json.error !== null) {
    throw new Error(json.error);
  }

  if (!response.ok) {
    throw new Error(json?.error || `Request failed with status ${response.status}`);
  }

  return json.data;
}

export const callsApi = {
  /** Fetches every stored call transcript, newest first. */
  async getCalls() {
    const response = await fetch(apiUrl('/calls'), {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    return handleResponse(response);
  },

  /** Fetches a single call transcript by its UUID. */
  async getCallById(id) {
    const response = await fetch(apiUrl(`/calls/${id}`), {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    return handleResponse(response);
  },

  /** Fetches the ordered per-turn conversation script (AI vs patient). */
  async getCallMessages(id) {
    const response = await fetch(apiUrl(`/calls/${id}/messages`), {
      method: 'GET',
      headers: { Accept: 'application/json' },
    });
    return handleResponse(response);
  },
};

export default callsApi;
