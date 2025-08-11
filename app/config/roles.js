// Role definitions and permissions for the health data exchange system

export const ROLES = {
  ADMIN: 'admin',
  HEALTHCARE_PROVIDER: 'healthcare_provider',
  PATIENT: 'patient',
};

export const PERMISSIONS = {
  // Data management permissions
  READ_PATIENT_DATA: 'read_patient_data',
  WRITE_PATIENT_DATA: 'write_patient_data',
  DELETE_PATIENT_DATA: 'delete_patient_data',
  
  // User management permissions
  MANAGE_USERS: 'manage_users',
  MANAGE_ROLES: 'manage_roles',
  
  // Healthcare specific permissions
  VIEW_ANALYTICS: 'view_analytics',
  SHARE_RECORDS: 'share_records',
  EXPORT_DATA: 'export_data',
  
  // Admin specific permissions
  SYSTEM_SETTINGS: 'system_settings',
  VIEW_AUDIT_LOGS: 'view_audit_logs',
};

// Role-based permission mapping
export const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.READ_PATIENT_DATA,
    PERMISSIONS.WRITE_PATIENT_DATA,
    PERMISSIONS.DELETE_PATIENT_DATA,
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.MANAGE_ROLES,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.SHARE_RECORDS,
    PERMISSIONS.EXPORT_DATA,
    PERMISSIONS.SYSTEM_SETTINGS,
    PERMISSIONS.VIEW_AUDIT_LOGS,
  ],
  [ROLES.HEALTHCARE_PROVIDER]: [
    PERMISSIONS.READ_PATIENT_DATA,
    PERMISSIONS.WRITE_PATIENT_DATA,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.SHARE_RECORDS,
    PERMISSIONS.EXPORT_DATA,
  ],
  [ROLES.PATIENT]: [
    PERMISSIONS.READ_PATIENT_DATA,
    PERMISSIONS.SHARE_RECORDS,
  ],
};

// Helper functions for role and permission checking
export const hasPermission = (userPermissions, requiredPermission) => {
  return userPermissions.includes(requiredPermission);
};

export const hasRole = (userRole, requiredRole) => {
  return userRole === requiredRole;
};

export const getPermissionsForRole = (role) => {
  return ROLE_PERMISSIONS[role] || [];
}; 