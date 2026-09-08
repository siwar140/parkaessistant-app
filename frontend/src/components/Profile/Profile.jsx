// frontend/src/components/Profile/Profile.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { updateProfile, updatePassword, uploadProfileImage, getProfileImageUrl } from '../../services/api';
import { CameraIcon, UserCircleIcon } from '@heroicons/react/24/outline';

const Profile = () => {
  const { user, refreshProfile } = useAuth();
  const fileInputRef = useRef(null);
  
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    hospital: '',
    specialty: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: ''
  });
  
  const [profileImage, setProfileImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name,
        phone: user.phone || '',
        hospital: user.hospital || '',
        specialty: user.specialty || ''
      });
      
      if (user.profile_image) {
        setProfileImage(getProfileImageUrl(user.id));
      }
    }
  }, [user]);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await updateProfile(formData);
      await refreshProfile();
      setSuccess('Profil mis à jour avec succès');
    } catch (err) {
      console.error('Erreur:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la mise à jour du profil');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await updatePassword(passwordData);
      setSuccess('Mot de passe mis à jour avec succès');
      setPasswordData({
        old_password: '',
        new_password: ''
      });
    } catch (err) {
      console.error('Erreur:', err);
      setError(err.response?.data?.detail || 'Erreur lors de la mise à jour du mot de passe');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await uploadProfileImage(file);
      await refreshProfile();
      setProfileImage(getProfileImageUrl(user.id));
      setSuccess('Photo de profil mise à jour avec succès');
    } catch (err) {
      console.error('Erreur:', err);
      setError(err.response?.data?.detail || 'Erreur lors de l\'upload de la photo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Profil</h1>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg mb-4">
          {success}
        </div>
      )}

      {/* Photo de profil */}
      <div className="bg-white rounded-2xl p-6 mb-6">
        <h2 className="text-lg font-bold mb-4">Photo de profil</h2>
        <div className="flex items-center gap-6">
          <div className="relative">
            {profileImage ? (
              <img 
                src={profileImage} 
                alt="Photo de profil" 
                className="w-24 h-24 rounded-full object-cover border-4 border-blue-100"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center">
                <UserCircleIcon className="w-16 h-16 text-blue-400" />
              </div>
            )}
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="absolute bottom-0 right-0 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
              title="Changer la photo"
            >
              <CameraIcon className="w-4 h-4" />
            </button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleImageUpload}
              className="hidden"
            />
          </div>
          
          <div>
            <p className="text-sm text-slate-600">Formats acceptés : JPEG, PNG, WEBP</p>
            <p className="text-xs text-slate-400 mt-1">Cliquez sur l'icône pour changer la photo</p>
          </div>
        </div>
      </div>

      {/* Formulaire Profil */}
      <form onSubmit={handleProfileSubmit} className="bg-white rounded-2xl p-6 mb-6">
        <h2 className="text-lg font-bold mb-4">Informations personnelles</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nom complet</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Téléphone</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hôpital</label>
            <input
              type="text"
              value={formData.hospital}
              onChange={(e) => setFormData({...formData, hospital: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Spécialité</label>
            <input
              type="text"
              value={formData.specialty}
              onChange={(e) => setFormData({...formData, specialty: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>
        <button type="submit" disabled={loading} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Mise à jour...' : 'Mettre à jour'}
        </button>
      </form>

      {/* Formulaire Mot de passe */}
      <form onSubmit={handlePasswordSubmit} className="bg-white rounded-2xl p-6">
        <h2 className="text-lg font-bold mb-4">Changer le mot de passe</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ancien mot de passe</label>
            <input
              type="password"
              value={passwordData.old_password}
              onChange={(e) => setPasswordData({...passwordData, old_password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nouveau mot de passe</label>
            <input
              type="password"
              value={passwordData.new_password}
              onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>
        <button type="submit" disabled={loading} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Mise à jour...' : 'Changer le mot de passe'}
        </button>
      </form>
    </div>
  );
};

export default Profile;