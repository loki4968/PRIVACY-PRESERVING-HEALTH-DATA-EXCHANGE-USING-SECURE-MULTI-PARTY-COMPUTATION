import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Profile from './components/Profile';
import ChangePassword from './components/ChangePassword';
import HealthDataUpload from './components/HealthDataUpload';
import SecureComputation from './components/SecureComputation';
import MLDashboard from './components/MLDashboard';
import FederatedLearning from './components/FederatedLearning';
import RiskAssessment from './components/RiskAssessment';
import TimeSeriesAnalysis from './components/TimeSeriesAnalysis';
import PatientReportRequest from './components/PatientReportRequest';
import Navigation from './components/Navigation';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            }
          />
          <Route
            path="/change-password"
            element={
              <PrivateRoute>
                <ChangePassword />
              </PrivateRoute>
            }
          />
          <Route
            path="/health-data"
            element={
              <PrivateRoute>
                <HealthDataUpload />
              </PrivateRoute>
            }
          />
          <Route
            path="/secure-computation"
            element={
              <PrivateRoute>
                <SecureComputation />
              </PrivateRoute>
            }
          />
          <Route
            path="/ml-dashboard"
            element={
              <PrivateRoute>
                <MLDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/federated-learning"
            element={
              <PrivateRoute>
                <FederatedLearning />
              </PrivateRoute>
            }
          />
          <Route
            path="/risk-assessment"
            element={
              <PrivateRoute>
                <RiskAssessment />
              </PrivateRoute>
            }
          />
          <Route
            path="/time-series"
            element={
              <PrivateRoute>
                <TimeSeriesAnalysis />
              </PrivateRoute>
            }
          />
          <Route
            path="/report-requests"
            element={
              <PrivateRoute>
                <PatientReportRequest />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;