"use client";

import React, { useState } from 'react';
import { Settings, Bell, Lock, Globe, Moon, Sun, Save } from 'lucide-react';
import { motion } from 'framer-motion';
import { CustomButton } from './ui/custom-button';
import { toast } from 'react-hot-toast';

const SettingsPanel = () => {
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      updates: false
    },
    privacy: {
      shareData: false,
      analytics: true
    },
    appearance: {
      theme: 'light',
      compactMode: false
    },
    language: 'en'
  });

  const [saving, setSaving] = useState(false);

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const settingsSections = [
    {
      id: 'notifications',
      title: 'Notifications',
      icon: <Bell className="w-5 h-5" />,
      settings: [
        {
          id: 'email',
          label: 'Email Notifications',
          description: 'Receive email updates about your uploads and data sharing'
        },
        {
          id: 'push',
          label: 'Push Notifications',
          description: 'Get instant notifications in your browser'
        },
        {
          id: 'updates',
          label: 'Product Updates',
          description: 'Stay informed about new features and improvements'
        }
      ]
    },
    {
      id: 'privacy',
      title: 'Privacy & Security',
      icon: <Lock className="w-5 h-5" />,
      settings: [
        {
          id: 'shareData',
          label: 'Share Usage Data',
          description: 'Help us improve by sharing anonymous usage data'
        },
        {
          id: 'analytics',
          label: 'Analytics',
          description: 'Allow analytics to track feature usage'
        }
      ]
    },
    {
      id: 'appearance',
      title: 'Appearance',
      icon: <Moon className="w-5 h-5" />,
      settings: [
        {
          id: 'theme',
          label: 'Theme',
          description: 'Choose between light and dark mode',
          type: 'select',
          options: [
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' },
            { value: 'system', label: 'System' }
          ]
        },
        {
          id: 'compactMode',
          label: 'Compact Mode',
          description: 'Use a more compact layout'
        }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      {/* Settings Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Settings className="w-6 h-6 text-gray-500" />
          <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
        </div>
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

      {/* Settings Sections */}
      <div className="grid gap-6">
        {settingsSections.map((section) => (
          <motion.div
            key={section.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 bg-gray-100 rounded-lg">
                {section.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
            </div>

            <div className="space-y-4">
              {section.settings.map((setting) => (
                <div key={setting.id} className="flex items-start justify-between">
                  <div>
                    <label
                      htmlFor={setting.id}
                      className="text-sm font-medium text-gray-900"
                    >
                      {setting.label}
                    </label>
                    <p className="text-sm text-gray-500">{setting.description}</p>
                  </div>

                  {setting.type === 'select' ? (
                    <select
                      id={setting.id}
                      value={settings[section.id][setting.id]}
                      onChange={(e) =>
                        handleSettingChange(section.id, setting.id, e.target.value)
                      }
                      className="ml-4 rounded-lg border border-gray-300 text-sm focus:ring-blue-500 focus:border-blue-500"
                    >
                      {setting.options.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        id={setting.id}
                        checked={settings[section.id][setting.id]}
                        onChange={(e) =>
                          handleSettingChange(section.id, setting.id, e.target.checked)
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default SettingsPanel; 