import axios from 'axios';

// In production, use empty string to make requests relative to current origin
// In development, VITE_API_URL will be set to http://localhost:8000
const API_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;

// Resumes API
export const resumesApi = {
  getAll: () => apiClient.get('/api/resumes'),
  getActive: () => apiClient.get('/api/resumes/active'),
  getById: (id) => apiClient.get(`/api/resumes/${id}`),
  create: (data) => apiClient.post('/api/resumes', data),
  update: (id, data) => apiClient.put(`/api/resumes/${id}`, data),
  delete: (id) => apiClient.delete(`/api/resumes/${id}`),
};

// Applications API
export const applicationsApi = {
  getAll: (params) => apiClient.get('/api/applications', { params }),
  getById: (id) => apiClient.get(`/api/applications/${id}`),
  create: (data) => apiClient.post('/api/applications', data),
  update: (id, data) => apiClient.put(`/api/applications/${id}`, data),
  delete: (id) => apiClient.delete(`/api/applications/${id}`),
  getHistory: (id) => apiClient.get(`/api/applications/${id}/history`),
};

// Leads API
export const leadsApi = {
  getAll: (params) => apiClient.get('/api/leads', { params }),
  getById: (id) => apiClient.get(`/api/leads/${id}`),
  create: (data) => apiClient.post('/api/leads', data),
  update: (id, data) => apiClient.put(`/api/leads/${id}`, data),
  delete: (id) => apiClient.delete(`/api/leads/${id}`),
  analyze: (id, resumeId) => apiClient.post(`/api/leads/${id}/analyze`, null, {
    params: { resume_id: resumeId }
  }),
  promote: (id) => apiClient.post(`/api/leads/${id}/promote`),
};
