"use client";

// Session management utility

const SESSION_DURATION = 30 * 60 * 1000; // 30 minutes
const ACTIVITY_TIMEOUT = 15 * 60 * 1000; // 15 minutes
const SESSION_KEY = 'session_data';
const ACTIVITY_KEY = 'last_activity';

export class SessionManager {
  constructor() {
    if (typeof window !== 'undefined') {
      this.setupActivityTracking();
    }
  }

  // Initialize a new session
  initSession(userData) {
    const sessionData = {
      userId: userData.id,
      role: userData.role,
      sessionId: this.generateSessionId(),
      startTime: Date.now(),
      expiresAt: Date.now() + SESSION_DURATION,
    };

    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    this.updateLastActivity();
    return sessionData;
  }

  // Generate unique session ID
  generateSessionId() {
    return 'sess_' + Math.random().toString(36).substr(2, 9);
  }

  // Update last activity timestamp
  updateLastActivity() {
    localStorage.setItem(ACTIVITY_KEY, Date.now().toString());
  }

  // Check if session is valid
  isSessionValid() {
    try {
      const sessionData = JSON.parse(localStorage.getItem(SESSION_KEY));
      const lastActivity = parseInt(localStorage.getItem(ACTIVITY_KEY));

      if (!sessionData || !lastActivity) {
        return false;
      }

      const now = Date.now();
      const isExpired = now > sessionData.expiresAt;
      const isInactive = now - lastActivity > ACTIVITY_TIMEOUT;

      return !isExpired && !isInactive;
    } catch (error) {
      console.error('Session validation error:', error);
      return false;
    }
  }

  // Setup activity tracking
  setupActivityTracking() {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    
    const activityHandler = () => {
      if (this.isSessionValid()) {
        this.updateLastActivity();
      }
    };

    events.forEach(event => {
      window.addEventListener(event, activityHandler, { passive: true });
    });
  }

  // Get current session data
  getSessionData() {
    try {
      return JSON.parse(localStorage.getItem(SESSION_KEY));
    } catch {
      return null;
    }
  }

  // Extend session
  extendSession() {
    const sessionData = this.getSessionData();
    if (sessionData) {
      sessionData.expiresAt = Date.now() + SESSION_DURATION;
      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    }
  }

  // End session
  endSession() {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(ACTIVITY_KEY);
  }
  
  // Check for concurrent sessions
  static async checkConcurrentSessions() {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        return true; // No session to check
      }

      const response = await fetch(`${API_BASE_URL}/check-session`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // If the endpoint doesn't exist or returns 404, consider it a success
      if (response.status === 404) {
        return true;
      }

      if (!response.ok) {
        return false;
      }
      
      const data = await response.json();
      return !data.hasConcurrentSession;
    } catch (error) {
      console.error('Error checking concurrent sessions:', error);
      return true; // Default to allowing login on error
    }
  }
}

// Export a singleton instance
const sessionManagerInstance = typeof window !== 'undefined' ? new SessionManager() : null;

// Export getToken function for services to use
export const getToken = () => {
  if (typeof window === 'undefined') return null;
  
  // First try to get token from localStorage directly
  const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
  if (token) return token;
  
  // If not found, try to get from session data
  if (sessionManagerInstance) {
    const sessionData = sessionManagerInstance.getSessionData();
    if (sessionData && sessionData.token) return sessionData.token;
  }
  
  return null;
}

// Check if session is valid
export const checkSession = async () => {
  try {
    const token = getToken();
    if (!token) return false;
    
    const response = await fetch('/api/auth/check-session', {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    if (!response.ok) {
      // Don't treat session check failures as critical errors
      console.warn('Session check skipped:', response.status);
      return true;
    }

    const data = await response.json();
    return data.valid !== false; // Consider session valid unless explicitly marked invalid
  } catch (error) {
    // Don't fail on session check errors
    console.warn('Session check error:', error);
    return true;
  }
}

export const sessionManager = new SessionManager();