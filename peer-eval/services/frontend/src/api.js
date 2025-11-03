import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: (userId) => api.get(`/auth/me?user_id=${userId}`),
};

export const usersAPI = {
  list: () => api.get('/users/'),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users/', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
};

export const projectsAPI = {
  list: (params) => api.get('/projects/', { params }),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects/', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

export const teamsAPI = {
  list: (params) => api.get('/teams/', { params }),
  get: (id) => api.get(`/teams/${id}`),
  create: (data) => api.post('/teams/', data),
  update: (id, data) => api.put(`/teams/${id}`, data),
  delete: (id) => api.delete(`/teams/${id}`),
  addMember: (teamId, data) => api.post(`/teams/${teamId}/members`, data),
  removeMember: (teamId, userId) => api.delete(`/teams/${teamId}/members/${userId}`),
};

export const formsAPI = {
  list: (params) => api.get('/forms/', { params }),
  get: (id) => api.get(`/forms/${id}`),
  create: (data) => api.post('/forms/', data),
  update: (id, data) => api.put(`/forms/${id}`, data),
  delete: (id) => api.delete(`/forms/${id}`),
  addCriterion: (formId, data) => api.post(`/forms/${formId}/criteria`, data),
  updateCriterion: (formId, criterionId, data) => api.put(`/forms/${formId}/criteria/${criterionId}`, data),
  deleteCriterion: (formId, criterionId) => api.delete(`/forms/${formId}/criteria/${criterionId}`),
};

export const evaluationsAPI = {
  list: (params) => api.get('/evaluations/', { params }),
  get: (id) => api.get(`/evaluations/${id}`),
  create: (data) => api.post('/evaluations/', data),
  update: (id, data) => api.put(`/evaluations/${id}`, data),
  delete: (id) => api.delete(`/evaluations/${id}`),
};

export const reportsAPI = {
  project: (id) => api.get(`/reports/project/${id}`),
  team: (id) => api.get(`/reports/team/${id}`),
  user: (id) => api.get(`/reports/user/${id}`),
  form: (id) => api.get(`/reports/evaluation-form/${id}`),
};

export default api;
