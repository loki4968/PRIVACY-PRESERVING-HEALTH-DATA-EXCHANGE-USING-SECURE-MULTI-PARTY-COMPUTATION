import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  TimeScale
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';
import MLService from '../services/MLService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  TimeScale,
  Title,
  Tooltip,
  Legend
);

const TimeSeriesAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [datasetId, setDatasetId] = useState('');
  const [forecastMethod, setForecastMethod] = useState('comprehensive');
  const [forecastHorizon, setForecastHorizon] = useState(30);
  const [privacyBudget, setPrivacyBudget] = useState(0.1);
  const [forecastData, setForecastData] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [seasonality, setSeasonality] = useState(null);
  
  const handleGenerateForecast = async (e) => {
    e.preventDefault();
    if (!datasetId) {
      setError('Please enter a dataset ID');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      let response;
      
      switch (forecastMethod) {
        case 'linear':
          response = await MLService.generateLinearForecast(datasetId, forecastHorizon, privacyBudget);
          break;
        case 'exponential':
          response = await MLService.generateExponentialForecast(datasetId, forecastHorizon, privacyBudget);
          break;
        case 'holtwinters':
          response = await MLService.generateHoltWintersForecast(datasetId, forecastHorizon, privacyBudget);
          break;
        case 'comprehensive':
        default:
          response = await MLService.generateComprehensiveForecast(datasetId, forecastHorizon, privacyBudget);
          break;
      }
      
      setForecastData(response.forecast);
      setAnomalies(response.anomalies || []);
      setSeasonality(response.seasonality);
      
    } catch (err) {
      setError('Error generating forecast: ' + (err.message || 'Unknown error'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for demonstration
  useEffect(() => {
    if (!forecastData && !loading) {
      // Generate dates for the past 90 days and 30 days into the future
      const dates = [];
      const historicalValues = [];
      const forecastValues = [];
      const upperBound = [];
      const lowerBound = [];
      
      const today = new Date();
      
      // Historical data - past 90 days
      for (let i = 90; i >= 1; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(date.toISOString().split('T')[0]);
        
        // Generate some realistic looking health data with weekly patterns
        const baseValue = 120; // e.g., blood glucose level
        const weekday = date.getDay();
        const weekendEffect = (weekday === 0 || weekday === 6) ? 15 : 0; // higher on weekends
        const randomNoise = Math.random() * 10 - 5;
        const trendEffect = i * 0.05; // slight upward trend
        
        historicalValues.push(baseValue + weekendEffect + randomNoise - trendEffect);
        forecastValues.push(null); // no forecast for historical dates
        upperBound.push(null);
        lowerBound.push(null);
      }
      
      // Add anomalies
      const mockAnomalies = [
        { date: dates[20], value: historicalValues[20] + 30 },
        { date: dates[45], value: historicalValues[45] - 25 },
        { date: dates[70], value: historicalValues[70] + 35 }
      ];
      
      // Replace values with anomalies
      mockAnomalies.forEach(anomaly => {
        const index = dates.indexOf(anomaly.date);
        if (index !== -1) {
          historicalValues[index] = anomaly.value;
        }
      });
      
      // Forecast data - next 30 days
      for (let i = 1; i <= 30; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        dates.push(date.toISOString().split('T')[0]);
        
        const baseValue = 120;
        const weekday = date.getDay();
        const weekendEffect = (weekday === 0 || weekday === 6) ? 15 : 0;
        const randomNoise = Math.random() * 5 - 2.5; // less noise in forecast
        const trendEffect = (90 + i) * 0.05; // continuing the trend
        
        const forecastValue = baseValue + weekendEffect + randomNoise - trendEffect;
        historicalValues.push(null); // no historical data for future dates
        forecastValues.push(forecastValue);
        upperBound.push(forecastValue + 10 + i * 0.5); // increasing uncertainty
        lowerBound.push(forecastValue - 10 - i * 0.5);
      }
      
      const mockForecastData = {
        dates,
        historical: historicalValues,
        forecast: forecastValues,
        upperBound,
        lowerBound
      };
      
      setForecastData(mockForecastData);
      setAnomalies(mockAnomalies);
      setSeasonality({
        weekly: true,
        monthly: false,
        quarterly: false,
        strength: 0.75,
        dominantPeriod: 7
      });
    }
  }, [forecastData, loading]);

  // Prepare chart data
  const chartData = forecastData ? {
    labels: forecastData.dates,
    datasets: [
      {
        label: 'Historical Data',
        data: forecastData.historical,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.1
      },
      {
        label: 'Forecast',
        data: forecastData.forecast,
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderDash: [5, 5],
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.1
      },
      {
        label: 'Upper Bound',
        data: forecastData.upperBound,
        borderColor: 'rgba(54, 162, 235, 0.3)',
        backgroundColor: 'transparent',
        borderDash: [2, 2],
        pointRadius: 0,
        fill: false,
        tension: 0.1
      },
      {
        label: 'Lower Bound',
        data: forecastData.lowerBound,
        borderColor: 'rgba(54, 162, 235, 0.3)',
        backgroundColor: 'transparent',
        borderDash: [2, 2],
        pointRadius: 0,
        fill: '+1',
        tension: 0.1
      },
      {
        label: 'Anomalies',
        data: forecastData.dates.map(date => {
          const anomaly = anomalies.find(a => a.date === date);
          return anomaly ? anomaly.value : null;
        }),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 1)',
        pointRadius: 6,
        pointStyle: 'triangle',
        showLine: false
      }
    ]
  } : null;

  return (
    <Container className="py-4">
      <h2 className="mb-4">Time Series Analysis</h2>
      
      <Row className="mb-4">
        <Col md={12}>
          <Card>
            <Card.Header>Forecast Configuration</Card.Header>
            <Card.Body>
              <Form onSubmit={handleGenerateForecast}>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Dataset ID</Form.Label>
                      <Form.Control 
                        type="text" 
                        placeholder="Enter dataset ID" 
                        value={datasetId}
                        onChange={(e) => setDatasetId(e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Forecast Method</Form.Label>
                      <Form.Select 
                        value={forecastMethod}
                        onChange={(e) => setForecastMethod(e.target.value)}
                      >
                        <option value="comprehensive">Comprehensive (Multiple Models)</option>
                        <option value="linear">Linear Regression</option>
                        <option value="exponential">Exponential Smoothing</option>
                        <option value="holtwinters">Holt-Winters</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Forecast Horizon (Days): {forecastHorizon}</Form.Label>
                      <Form.Range 
                        min={7} 
                        max={90} 
                        step={1} 
                        value={forecastHorizon}
                        onChange={(e) => setForecastHorizon(parseInt(e.target.value))}
                      />
                    </Form.Group>
                  </Col>
                  
                  <Col md={6}>
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
                  </Col>
                </Row>
                
                <Button 
                  variant="primary" 
                  type="submit" 
                  disabled={loading}
                >
                  {loading ? 'Generating...' : 'Generate Forecast'}
                </Button>
              </Form>
              
              {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {forecastData && (
        <Row>
          <Col md={12}>
            <Card className="mb-4">
              <Card.Header>Time Series Forecast</Card.Header>
              <Card.Body>
                <div style={{ height: '400px' }}>
                  <Line 
                    data={chartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      interaction: {
                        mode: 'index',
                        intersect: false,
                      },
                      plugins: {
                        tooltip: {
                          callbacks: {
                            title: function(context) {
                              return context[0].label;
                            },
                            label: function(context) {
                              if (context.dataset.label === 'Anomalies' && context.raw !== null) {
                                return 'Anomaly: ' + context.raw.toFixed(2);
                              }
                              return context.dataset.label + ': ' + (context.raw !== null ? context.raw.toFixed(2) : 'N/A');
                            }
                          }
                        },
                        legend: {
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: 'Time Series Forecast with Privacy-Preserving Analytics'
                        }
                      },
                      scales: {
                        x: {
                          type: 'category',
                          title: {
                            display: true,
                            text: 'Date'
                          }
                        },
                        y: {
                          title: {
                            display: true,
                            text: 'Value'
                          },
                          suggestedMin: Math.min(...forecastData.historical.filter(v => v !== null), ...forecastData.forecast.filter(v => v !== null)) - 20,
                          suggestedMax: Math.max(...forecastData.historical.filter(v => v !== null), ...forecastData.forecast.filter(v => v !== null)) + 20
                        }
                      }
                    }}
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
      
      {seasonality && (
        <Row>
          <Col md={6}>
            <Card className="mb-4">
              <Card.Header>Seasonality Analysis</Card.Header>
              <Card.Body>
                <p><strong>Seasonality Strength:</strong> {(seasonality.strength * 100).toFixed(1)}%</p>
                <p><strong>Dominant Period:</strong> {seasonality.dominantPeriod} days</p>
                <p><strong>Detected Patterns:</strong></p>
                <ul>
                  {seasonality.weekly && <li>Weekly pattern detected</li>}
                  {seasonality.monthly && <li>Monthly pattern detected</li>}
                  {seasonality.quarterly && <li>Quarterly pattern detected</li>}
                  {!seasonality.weekly && !seasonality.monthly && !seasonality.quarterly && 
                    <li>No significant seasonal patterns detected</li>}
                </ul>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={6}>
            <Card>
              <Card.Header>Anomaly Detection</Card.Header>
              <Card.Body>
                <p><strong>Detected Anomalies:</strong> {anomalies.length}</p>
                {anomalies.length > 0 ? (
                  <ul className="list-group">
                    {anomalies.map((anomaly, index) => (
                      <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                          <strong>Date:</strong> {anomaly.date}
                        </div>
                        <div>
                          <strong>Value:</strong> {anomaly.value.toFixed(2)}
                        </div>
                        <span className="badge bg-danger rounded-pill">Anomaly</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No anomalies detected in the time series data.</p>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default TimeSeriesAnalysis;