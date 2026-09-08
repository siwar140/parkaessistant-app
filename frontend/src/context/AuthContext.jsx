// frontend/src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as loginApi, register as registerApi, getProfile } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Vérifier si un token existe dans localStorage
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('doctor');
        
        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          
          // Vérifier si le token est encore valide
          try {
            const profile = await getProfile();
            setUser(profile);
            localStorage.setItem('doctor', JSON.stringify(profile));
          } catch (error) {
            // Token invalide ou expiré
            localStorage.removeItem('access_token');
            localStorage.removeItem('doctor');
            setToken(null);
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Erreur lors de l\'initialisation de l\'auth:', error);
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
  }, []);

  // Écouter les changements de localStorage (pour synchroniser entre onglets)
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'access_token' && !e.newValue) {
        setToken(null);
        setUser(null);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await loginApi(email, password);
      
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('doctor', JSON.stringify(response.doctor));
      
      setToken(response.access_token);
      setUser(response.doctor);
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await registerApi(userData);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('doctor');
    
    setToken(null);
    setUser(null);
    
    window.location.href = '/login';
  };

  const refreshProfile = async () => {
    if (token) {
      try {
        const profile = await getProfile();
        setUser(profile);
        localStorage.setItem('doctor', JSON.stringify(profile));
        return profile;
      } catch (error) {
        throw error;
      }
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      logout,
      refreshProfile,
      isAuthenticated: !!user,
    }}>
      {children}
    </AuthContext.Provider>
  );
};