// frontend/src/services/api.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('doctor');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ AUTH ============
export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

// ============ VERIFICATION ============
export const sendVerificationCode = async (email, purpose = 'registration') => {
  const response = await api.post('/verification/send-code', { email, purpose });
  return response.data;
};

export const verifyCode = async (email, code, purpose = 'registration') => {
  const response = await api.post('/verification/verify-code', { email, code, purpose });
  return response.data;
};

// ============ RESET PASSWORD ============
export const sendResetPasswordCode = async (email) => {
  const response = await api.post('/verification/send-code', { 
    email, 
    purpose: 'reset_password' 
  });
  return response.data;
};

export const resetPassword = async (email, code, newPassword) => {
  const response = await api.post('/auth/reset-password', { 
    email, 
    code, 
    new_password: newPassword 
  });
  return response.data;
};

// ============ DOCTOR ============
export const getProfile = async () => {
  const response = await api.get('/doctor/profile');
  return response.data;
};

export const updateProfile = async (profileData) => {
  const response = await api.put('/doctor/profile', profileData);
  return response.data;
};

export const updatePassword = async (passwordData) => {
  const response = await api.put('/doctor/password', passwordData);
  return response.data;
};

// ✅ Upload photo de profil
export const uploadProfileImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.put('/doctor/profile-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// ✅ Récupérer l'URL de la photo avec doctorId
export const getProfileImageUrl = (doctorId) => {
  return `${API_URL}/doctor/profile-image/${doctorId}`;
};

// ============ PATIENTS ============
export const getPatients = async (search = '') => {
  const response = await api.get('/patients', {
    params: { search },
  });
  return response.data;
};

export const getPatient = async (id) => {
  const response = await api.get(`/patients/${id}`);
  return response.data;
};

export const createPatient = async (patientData) => {
  const response = await api.post('/patients', patientData);
  return response.data;
};

export const updatePatient = async (id, patientData) => {
  const response = await api.put(`/patients/${id}`, patientData);
  return response.data;
};

export const deletePatient = async (id) => {
  const response = await api.delete(`/patients/${id}`);
  return response.data;
};

export const getPatientAnalyses = async (patientId) => {
  if (!patientId) return [];
  const response = await api.get('/predictions/history', {
    params: { patient_id: patientId },
  });
  return response.data;
};

// ============ PREDICTIONS ============
export const getHistory = async (patientId = null) => {
  const params = patientId ? { patient_id: patientId } : {};
  const response = await api.get('/predictions/history', { params });
  return response.data;
};

export const getPrediction = async (id) => {
  const response = await api.get(`/predictions/${id}`);
  return response.data;
};

export const deletePrediction = async (id) => {
  const response = await api.delete(`/predictions/${id}`);
  return response.data;
};

export const predictAudio = async (audioFile, patientId = null, patientName = null, notes = null) => {
  const formData = new FormData();
  formData.append('file', audioFile);
  
  if (patientId) {
    formData.append('patient_id', patientId);
  }
  
  if (patientName) {
    formData.append('patient_name', patientName);
  }
  
  if (notes) {
    formData.append('notes', notes);
  }

  const response = await api.post('/predictions/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export default api;