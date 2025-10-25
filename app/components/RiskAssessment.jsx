import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, ProgressBar } from 'react-bootstrap';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import MLService from '../services/MLService';

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const RiskAssessment = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [patientId, setPatientId] = useState('');
  const [riskScore, setRiskScore] = useState(null);
  const [riskFactors, setRiskFactors] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [populationRisk, setPopulationRisk] = useState(null);
  const [privacyBudget, setPrivacyBudget] = useState(0.1);
  
  // Risk category colors
  const riskColors = {
    low: '#28a745',     // Green
    moderate: '#ffc107', // Yellow
    high: '#dc3545',    // Red
    veryHigh: '#721c24' // Dark red
  };

  const getRiskColor = (score) => {
    if (score < 25) return riskColors.low;
    if (score < 50) return riskColors.moderate;
    if (score < 75) return riskColors.high;
    return riskColors.veryHigh;
  };

  const getRiskCategory = (score) => {
    if (score < 25) return 'Low Risk';
    if (score < 50) return 'Moderate Risk';
    if (score < 75) return 'High Risk';
    return 'Very High Risk';
  };

  const handleCalculateRisk = async (e) => {
    e.preventDefault();
    if (!patientId) {
      setError('Please enter a patient ID');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      // In a real application, we would pass actual health metrics
      // For demo purposes, we're just passing the patient ID
      const response = await MLService.calculateRiskScore(patientId, privacyBudget);
      
      setRiskScore(response.riskScore);
      setRiskFactors(response.riskFactors);
      setRecommendations(response.recommendations);
      
      // Also fetch population risk for comparison
      const popRisk = await MLService.calculatePopulationRisk(privacyBudget);
      setPopulationRisk(popRisk);
      
    } catch (err) {
      setError('Error calculating risk: ' + (err.message || 'Unknown error'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for demonstration
  useEffect(() => {
    if (!riskScore && !loading) {
      // Set mock data for demonstration
      const mockRiskScore = 65;
      const mockRiskFactors = [
        { factor: 'Blood Pressure', value: 'High (145/95)', impact: 'High' },
        { factor: 'BMI', value: '32.5', impact: 'Moderate' },
        { factor: 'Smoking Status', value: 'Current Smoker', impact: 'High' },
        { factor: 'Physical Activity', value: 'Low', impact: 'Moderate' },
        { factor: 'Family History', value: 'Cardiovascular Disease', impact: 'High' }
      ];
      const mockRecommendations = [
        'Consult with a healthcare provider about blood pressure management',
        'Consider a structured weight management program',
        'Smoking cessation program recommended',
        'Increase physical activity to at least 150 minutes per week',
        'Schedule regular cardiovascular screenings'
      ];
      const mockPopulationRisk = {
        distribution: {
          'Low Risk': 45,
          'Moderate Risk': 30,
          'High Risk': 20,
          'Very High Risk': 5
        },
        averageScore: 35
      };
      
      setRiskScore(mockRiskScore);
      setRiskFactors(mockRiskFactors);
      setRecommendations(mockRecommendations);
      setPopulationRisk(mockPopulationRisk);
    }
  }, [riskScore, loading]);

  // Prepare chart data
  const pieChartData = {
    labels: populationRisk ? Object.keys(populationRisk.distribution) : [],
    datasets: [
      {
        data: populationRisk ? Object.values(populationRisk.distribution) : [],
        backgroundColor: [
          riskColors.low,
          riskColors.moderate,
          riskColors.high,
          riskColors.veryHigh
        ],
        borderWidth: 1,
      },
    ],
  };

  const riskFactorsChartData = {
    labels: riskFactors.map(factor => factor.factor),
    datasets: [
      {
        label: 'Risk Impact',
        data: riskFactors.map(factor => {
          switch(factor.impact) {
            case 'Low': return 25;
            case 'Moderate': return 50;
            case 'High': return 75;
            case 'Very High': return 100;
            default: return 0;
          }
        }),
        backgroundColor: riskFactors.map(factor => {
          switch(factor.impact) {
            case 'Low': return riskColors.low;
            case 'Moderate': return riskColors.moderate;
            case 'High': return riskColors.high;
            case 'Very High': return riskColors.veryHigh;
            default: return '#6c757d';
          }
        }),
      },
    ],
  };

  return (
    <Container className="py-4">
      <h2 className="mb-4">Risk Assessment</h2>
      
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>Patient Risk Assessment</Card.Header>
            <Card.Body>
              <Form onSubmit={handleCalculateRisk}>
                <Form.Group className="mb-3">
                  <Form.Label>Patient ID</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="Enter patient ID" 
                    value={patientId}
                    onChange={(e) => setPatientId(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Privacy Budget (ε): {privacyBudget}</Form.Label>
                  <Form.Range 
                    min={0.01} 
                    max={1} 
                    step={0.01} 
                    value={privacyBudget}
                    onChange={(e) => setPrivacyBudget(parseFloat(e.target.value))}
                  />
                  <Form.Text className="text-muted">
                    Lower values provide stronger privacy but may reduce accuracy
                  </Form.Text>
                </Form.Group>
                
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={loading}
                >
                  {loading ? 'Calculating...' : 'Calculate Risk'}
                </Button>
              </Form>
              
              {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            </Card.Body>
          </Card>
        </Col>
        
        {riskScore !== null && (
          <Col md={6}>
            <Card>
              <Card.Header>Risk Score</Card.Header>
              <Card.Body>
                <h3 className="text-center mb-3">{getRiskCategory(riskScore)}</h3>
                <ProgressBar 
                  now={riskScore} 
                  label={`${riskScore}%`}
                  variant={riskScore < 25 ? 'success' : riskScore < 50 ? 'warning' : 'danger'}
                  className="mb-4"
                  style={{ height: '30px' }}
                />
                
                <p className="text-center">
                  This patient's risk score is {riskScore}%, which is classified as{' '}
                  <strong style={{ color: getRiskColor(riskScore) }}>
                    {getRiskCategory(riskScore)}
                  </strong>
                  {populationRisk && (
                    <>. The population average risk score is {populationRisk.averageScore}%.</>
                  )}
                </p>
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>
      
      {riskScore !== null && (
        <Row>
          <Col md={6}>
            <Card className="mb-4">
              <Card.Header>Risk Factors</Card.Header>
              <Card.Body>
                <div style={{ height: '300px' }}>
                  <Bar 
                    data={riskFactorsChartData}
                    options={{
                      indexAxis: 'y',
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        x: {
                          max: 100,
                          beginAtZero: true
                        }
                      }
                    }}
                  />
                </div>
                
                <div className="mt-3">
                  <h5>Detailed Risk Factors</h5>
                  <ul className="list-group">
                    {riskFactors.map((factor, index) => (
                      <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                          <strong>{factor.factor}</strong>: {factor.value}
                        </div>
                        <span 
                          className="badge rounded-pill" 
                          style={{
                            backgroundColor: 
                              factor.impact === 'High' ? riskColors.high :
                              factor.impact === 'Moderate' ? riskColors.moderate :
                              riskColors.low
                          }}
                        >
                          {factor.impact}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={6}>
            <Row>
              <Col md={12}>
                <Card className="mb-4">
                  <Card.Header>Population Risk Distribution</Card.Header>
                  <Card.Body>
                    <div style={{ height: '200px', position: 'relative' }}>
                      <Pie 
                        data={pieChartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false
                        }}
                      />
                    </div>
                  </Card.Body>
                </Card>
              </Col>
              
              <Col md={12}>
                <Card>
                  <Card.Header>Recommendations</Card.Header>
                  <Card.Body>
                    <ul className="list-group">
                      {recommendations.map((rec, index) => (
                        <li key={index} className="list-group-item">{rec}</li>
                      ))}
                    </ul>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default RiskAssessment;