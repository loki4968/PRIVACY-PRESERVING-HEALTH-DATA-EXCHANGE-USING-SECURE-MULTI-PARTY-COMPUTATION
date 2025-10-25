import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Table, Badge, Modal, Alert } from 'react-bootstrap';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { useNavigate } from 'react-router-dom';

const PatientReportRequest = () => {
  const navigate = useNavigate();
  const [organizations, setOrganizations] = useState([]);
  const [reportRequests, setReportRequests] = useState([]);
  const [selectedOrg, setSelectedOrg] = useState('');
  const [visitDate, setVisitDate] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showSecretCodeModal, setShowSecretCodeModal] = useState(false);
  const [currentSecretCode, setCurrentSecretCode] = useState('');
  const [secretCodeInput, setSecretCodeInput] = useState('');
  const [secretCodeError, setSecretCodeError] = useState(null);
  const [secretCodeSuccess, setSecretCodeSuccess] = useState(null);
  const [reportByCode, setReportByCode] = useState(null);

  // Fetch healthcare organizations
  useEffect(() => {
    const fetchOrganizations = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/report-requests/healthcare-organizations`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setOrganizations(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch healthcare organizations');
        setLoading(false);
    }
  };

  return (
    <Container className="mt-4">
      <h2>Patient Report Requests</h2>

      {/* Error and Success Alerts */}
      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Row className="mt-4">
        <Col md={6}>
          <Card>
            <Card.Header>Request a Report</Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Healthcare Organization</Form.Label>
                  <Form.Control
                    as="select"
                    value={selectedOrg}
                    onChange={(e) => setSelectedOrg(e.target.value)}
                    required
                  >
                    <option value="">Select an organization</option>
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name} ({org.type})
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Visit Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={visitDate}
                    onChange={(e) => setVisitDate(e.target.value)}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Description (Optional)</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe the reason for your request"
                  />
                </Form.Group>

                <Button variant="primary" type="submit" disabled={loading}>
                  {loading ? 'Submitting...' : 'Submit Request'}
                </Button>
              </Form>
            </Card.Body>
          </Card>

          <Card className="mt-4">
            <Card.Header>Access Report by Secret Code</Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Secret Code</Form.Label>
                  <Form.Control
                    type="text"
                    value={secretCodeInput}
                    onChange={(e) => setSecretCodeInput(e.target.value)}
                    placeholder="Enter the secret code"
                    required
                  />
                </Form.Group>

                <Button variant="primary" onClick={handleAccessByCode} disabled={loading}>
                  {loading ? 'Searching...' : 'Access Report'}
                </Button>
              </Form>

              {secretCodeError && <Alert variant="danger" className="mt-3">{secretCodeError}</Alert>}
              {secretCodeSuccess && <Alert variant="success" className="mt-3">{secretCodeSuccess}</Alert>}

              {reportByCode && (
                <Card className="mt-3">
                  <Card.Header>Report Details</Card.Header>
                  <Card.Body>
                    <p><strong>Organization:</strong> {reportByCode.organization_name}</p>
                    <p><strong>Visit Date:</strong> {new Date(reportByCode.visit_date).toLocaleDateString()}</p>
                    <p><strong>Status:</strong> <Badge variant={getStatusBadgeVariant(reportByCode.status)}>{reportByCode.status}</Badge></p>
                    {reportByCode.description && <p><strong>Description:</strong> {reportByCode.description}</p>}
                    {reportByCode.has_report && (
                      <Button variant="success" onClick={() => handleDownloadByCode(reportByCode.secret_code)}>
                        Download Report
                      </Button>
                    )}
                  </Card.Body>
                </Card>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>Your Report Requests</Card.Header>
            <Card.Body>
              {reportRequests.length === 0 ? (
                <p>You have no report requests yet.</p>
              ) : (
                <Table responsive>
                  <thead>
                    <tr>
                      <th>Organization</th>
                      <th>Visit Date</th>
                      <th>Status</th>
                      <th>Secret Code</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reportRequests.map((request) => (
                      <tr key={request.id}>
                        <td>{request.organization_name}</td>
                        <td>{new Date(request.visit_date).toLocaleDateString()}</td>
                        <td>
                          <Badge variant={getStatusBadgeVariant(request.status)}>
                            {request.status}
                          </Badge>
                        </td>
                        <td>
                          {request.secret_code}
                        </td>
                        <td>
                          {request.has_report && (
                            <Button
                              variant="success"
                              size="sm"
                              onClick={() => handleDownload(request.id)}
                            >
                              Download
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Secret Code Modal */}
      <Modal show={showSecretCodeModal} onHide={() => setShowSecretCodeModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Your Secret Code</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Please save this secret code. You can use it to access your report without logging in:</p>
          <Alert variant="info" className="text-center">
            <h4>{currentSecretCode}</h4>
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowSecretCodeModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

    fetchOrganizations();
  }, []);

  // Fetch report requests
  useEffect(() => {
    const fetchReportRequests = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/report-requests`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setReportRequests(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch report requests');
        setLoading(false);
      }
    };

    fetchReportRequests();
  }, []);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!selectedOrg || !visitDate) {
      setError('Please select an organization and visit date');
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/report-requests`,
        {
          organization_id: parseInt(selectedOrg),
          visit_date: visitDate,
          description: description
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // Add the new request to the list
      setReportRequests([response.data, ...reportRequests]);
      setSuccess('Report request created successfully! Your secret code is: ' + response.data.secret_code);
      setCurrentSecretCode(response.data.secret_code);
      setShowSecretCodeModal(true);
      
      // Reset form
      setSelectedOrg('');
      setVisitDate('');
      setDescription('');
      setLoading(false);
    } catch (err) {
      setError('Failed to create report request');
      setLoading(false);
    }
  };

  // Handle download report
  const handleDownload = async (requestId) => {
    try {
      const token = localStorage.getItem('token');
      window.open(`${API_BASE_URL}/report-requests/${requestId}/download?token=${token}`, '_blank');
    } catch (err) {
      setError('Failed to download report');
    }
  };

  // Handle access by secret code
  const handleAccessByCode = async () => {
    setSecretCodeError(null);
    setSecretCodeSuccess(null);
    setReportByCode(null);

    if (!secretCodeInput) {
      setSecretCodeError('Please enter a secret code');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE_URL}/report-requests/access-by-code`,
        { secret_code: secretCodeInput }
      );

      setReportByCode(response.data);
      setSecretCodeSuccess('Report found successfully!');
      setLoading(false);
    } catch (err) {
      setSecretCodeError('No report found with this secret code');
      setLoading(false);
    }
  };

  // Handle download by secret code
  const handleDownloadByCode = async (secretCode) => {
    try {
      window.open(`${API_BASE_URL}/report-requests/download-by-code/${secretCode}`, '_blank');
    } catch (err) {
      setSecretCodeError('Failed to download report');
    }
  };

  // Status badge color
  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'approved':
        return 'success';
      case 'rejected':
        return 'danger';
      default:
        return 'secondary';
    }
  };