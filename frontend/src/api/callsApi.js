const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
    const url = `${API_BASE_URL}/calls`;
    const res = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
    return handleResponse(res);
  },

  async getCallById(id) {
    const url = `${API_BASE_URL}/calls/${id}`;
    const res = await fetch(url, { method: 'GET', headers: { Accept: 'application/json' } });
    return handleResponse(res);
  }
};

export default callsApi;
