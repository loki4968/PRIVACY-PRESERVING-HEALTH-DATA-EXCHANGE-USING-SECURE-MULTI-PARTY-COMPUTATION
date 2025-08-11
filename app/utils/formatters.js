export const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  }).format(date);
};

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
};

// Function to analyze health metrics and detect potential issues
export const analyzeHealthMetrics = (data) => {
  const issues = [];
  
  // Blood pressure analysis
  if (data.systolic && data.diastolic) {
    if (data.systolic >= 140 || data.diastolic >= 90) {
      issues.push({
        type: 'warning',
        message: 'High blood pressure detected',
        details: `${data.systolic}/${data.diastolic} mmHg`,
        recommendation: 'Consider consulting a healthcare provider for blood pressure management.'
      });
    } else if (data.systolic < 90 || data.diastolic < 60) {
      issues.push({
        type: 'warning',
        message: 'Low blood pressure detected',
        details: `${data.systolic}/${data.diastolic} mmHg`,
        recommendation: 'Monitor for symptoms like dizziness and consult healthcare provider if concerned.'
      });
    }
  }

  // Blood sugar analysis
  if (data.blood_sugar) {
    if (data.blood_sugar > 200) {
      issues.push({
        type: 'danger',
        message: 'High blood sugar detected',
        details: `${data.blood_sugar} mg/dL`,
        recommendation: 'Urgent: Consult healthcare provider for diabetes management.'
      });
    } else if (data.blood_sugar < 70) {
      issues.push({
        type: 'danger',
        message: 'Low blood sugar detected',
        details: `${data.blood_sugar} mg/dL`,
        recommendation: 'Immediate action required: Consume fast-acting carbohydrates.'
      });
    }
  }

  // Heart rate analysis
  if (data.heart_rate) {
    if (data.heart_rate > 100) {
      issues.push({
        type: 'warning',
        message: 'Elevated heart rate detected',
        details: `${data.heart_rate} bpm`,
        recommendation: 'Monitor for other symptoms and consult healthcare provider if persistent.'
      });
    } else if (data.heart_rate < 60) {
      issues.push({
        type: 'warning',
        message: 'Low heart rate detected',
        details: `${data.heart_rate} bpm`,
        recommendation: 'If experiencing symptoms, consult healthcare provider.'
      });
    }
  }

  // Temperature analysis
  if (data.temperature) {
    if (data.temperature > 38) {
      issues.push({
        type: 'warning',
        message: 'Fever detected',
        details: `${data.temperature}°C`,
        recommendation: 'Monitor temperature and seek medical attention if persistent or worsening.'
      });
    }
  }

  // Lab results analysis
  if (data.lab_results) {
    Object.entries(data.lab_results).forEach(([test, value]) => {
      // Add specific lab result analysis based on test type
      switch(test.toLowerCase()) {
        case 'cholesterol':
          if (value > 200) {
            issues.push({
              type: 'warning',
              message: 'Elevated cholesterol levels',
              details: `${value} mg/dL`,
              recommendation: 'Consider lifestyle changes and consult healthcare provider.'
            });
          }
          break;
        case 'a1c':
          if (value > 6.5) {
            issues.push({
              type: 'warning',
              message: 'Elevated A1C levels',
              details: `${value}%`,
              recommendation: 'Indicates possible diabetes. Consult healthcare provider.'
            });
          }
          break;
      }
    });
  }

  return issues;
}; 