"use client";

import React, { useState } from 'react';
import { User, Mail, Building, Phone, MapPin, Camera, Save } from 'lucide-react';
import { motion } from 'framer-motion';
import { CustomButton } from './ui/custom-button';
import { toast } from 'react-hot-toast';

const UserProfile = ({ user }) => {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    organization: user?.organization || '',
    phone: user?.phone || '',
    location: user?.location || '',
    role: user?.role || '',
    avatar: user?.avatar || null
  });

  const handleInputChange = (field, value) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Profile updated successfully');
      setEditing(false);
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileData(prev => ({
          ...prev,
          avatar: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <User className="w-6 h-6 text-gray-500" />
          <h2 className="text-xl font-semibold text-gray-900">Profile</h2>
        </div>
        {editing ? (
          <div className="flex items-center space-x-3">
            <CustomButton
              onClick={() => setEditing(false)}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700"
            >
              Cancel
            </CustomButton>
            <CustomButton
              onClick={handleSave}
              disabled={saving}
              className={`flex items-center space-x-2 ${
                saving ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {saving ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  <span>Save Changes</span>
                </>
              )}
            </CustomButton>
          </div>
        ) : (
          <CustomButton
            onClick={() => setEditing(true)}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700"
          >
            Edit Profile
          </CustomButton>
        )}
      </div>

      {/* Profile Content */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        {/* Avatar Section */}
        <div className="flex items-center space-x-6 mb-8">
          <div className="relative">
            <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
              {profileData.avatar ? (
                <img
                  src={profileData.avatar}
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              ) : (
                <User className="w-12 h-12 text-gray-400" />
              )}
            </div>
            {editing && (
              <label
                htmlFor="avatar-upload"
                className="absolute bottom-0 right-0 p-1 bg-white rounded-full border border-gray-200 cursor-pointer hover:bg-gray-50"
              >
                <Camera className="w-4 h-4 text-gray-500" />
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarChange}
                />
              </label>
            )}
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-900">{profileData.name}</h3>
            <p className="text-sm text-gray-500">{profileData.role}</p>
          </div>
        </div>

        {/* Profile Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { icon: User, label: 'Full Name', field: 'name' },
            { icon: Mail, label: 'Email', field: 'email' },
            { icon: Building, label: 'Organization', field: 'organization' },
            { icon: Phone, label: 'Phone', field: 'phone' },
            { icon: MapPin, label: 'Location', field: 'location' }
          ].map((item) => (
            <div key={item.field} className="space-y-2">
              <label className="flex items-center space-x-2 text-sm text-gray-500">
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </label>
              {editing ? (
                <input
                  type="text"
                  value={profileData[item.field]}
                  onChange={(e) => handleInputChange(item.field, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              ) : (
                <p className="text-gray-900">{profileData[item.field] || 'Not set'}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Additional Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Member Since</p>
            <p className="font-medium">January 2024</p>
          </div>
          <div>
            <p className="text-gray-500">Last Login</p>
            <p className="font-medium">Today at 10:30 AM</p>
          </div>
          <div>
            <p className="text-gray-500">Account Type</p>
            <p className="font-medium">Healthcare Provider</p>
          </div>
          <div>
            <p className="text-gray-500">Status</p>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Active
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default UserProfile; 