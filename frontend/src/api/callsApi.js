import { apiUrl } from './config';

// API base URL + path builder come from the shared env-driven config (see config.js).

async function handleResponse(response) {
  let json;
  try {
    json = await response.json();
  } catch (err) {
    throw new Error(`Failed to parse server response: ${response.statusText}`);
  }
  if (json && json.hasOwnProperty('error') && json.error !== null) {
    throw new Error(json.error);
  }
  if (!response.ok) {
    throw new Error(json?.error || `Request failed with status ${response.status}`);
  }
  return json.data;
}

export const callsApi = {
  async getCalls() {
    const url = apiUrl('/calls');
    const res = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
    return handleResponse(res);
  },

  async getCallById(id) {
    const url = apiUrl(`/calls/${id}`);
    const res = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
    return handleResponse(res);
  },

  /**
   * Fetches the turn-by-turn conversation script (AI vs patient) for a call.
   */
  async getCallMessages(id) {
    const url = apiUrl(`/calls/${id}/messages`);
    const res = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
    return handleResponse(res);
  }
};

export default callsApi;
