const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Common helper to parse response envelopes and throw clean errors.
 */
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

export const patientsApi = {
  /**
   * Fetches patients with optional query filters.
   */
  async getPatients({ last_name = '', date_of_birth = '', phone_number = '' } = {}) {
    const params = new URLSearchParams();
    if (last_name) params.append('last_name', last_name);
    if (date_of_birth) params.append('date_of_birth', date_of_birth);
    if (phone_number) params.append('phone_number', phone_number);

    const url = `${API_BASE_URL}/patients?${params.toString()}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });
    return handleResponse(response);
  },

  /**
   * Fetches a single patient by UUID.
   */
  async getPatientById(id) {
    const url = `${API_BASE_URL}/patients/${id}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });
    return handleResponse(response);
  },

  /**
   * Creates a new patient registration record.
   */
  async createPatient(patientData) {
    const url = `${API_BASE_URL}/patients`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(patientData)
    });
    return handleResponse(response);
  },

  /**
   * Updates an existing patient record partially.
   */
  async updatePatient(id, patientData) {
    const url = `${API_BASE_URL}/patients/${id}`;
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(patientData)
    });
    return handleResponse(response);
  },

  /**
   * Triggers soft-deletion of a patient record.
   */
  async deletePatient(id) {
    const url = `${API_BASE_URL}/patients/${id}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      }
    });
    return handleResponse(response);
  },

  /**
   * Retrieves voice logs/transcripts related to a patient.
   */
  async getPatientTranscripts(id) {
    const url = `${API_BASE_URL}/patients/${id}/transcripts`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });
    return handleResponse(response);
  }
};
export default patientsApi;
