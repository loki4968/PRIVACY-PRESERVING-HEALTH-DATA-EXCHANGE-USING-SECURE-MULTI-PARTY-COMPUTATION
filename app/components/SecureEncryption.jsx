import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';

const SecureEncryption = ({ computationId, onEncryptionComplete }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [encryptionParams, setEncryptionParams] = useState(null);
  const [dataToEncrypt, setDataToEncrypt] = useState('');
  const [encryptedData, setEncryptedData] = useState(null);
  const { user } = useAuth();
  const token = user?.token;

  const fetchEncryptionParams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/secure-computations/${computationId}/client-encrypt`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch encryption parameters');
      }

      const data = await response.json();
      setEncryptionParams(data);
      toast.success('Encryption parameters fetched successfully');
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const encryptData = () => {
    if (!encryptionParams) {
      toast.error('Please fetch encryption parameters first');
      return;
    }

    if (!dataToEncrypt) {
      toast.error('Please enter data to encrypt');
      return;
    }

    setIsLoading(true);
    try {
      // Parse the input data
      const dataPoints = dataToEncrypt.split(',').map(item => parseFloat(item.trim()));
      
      // Check for invalid data
      if (dataPoints.some(isNaN)) {
        throw new Error('Invalid data format. Please enter comma-separated numbers.');
      }

      let result;
      
      // Encrypt based on encryption type
      if (encryptionParams.encryption_type === 'homomorphic') {
        result = encryptHomomorphic(dataPoints, encryptionParams);
      } else if (encryptionParams.encryption_type === 'hybrid') {
        result = encryptHybrid(dataPoints, encryptionParams);
      } else {
        // Standard encryption (placeholder - in real app would use proper encryption)
        result = {
          encryption_type: 'standard',
          data: dataPoints
        };
      }

      setEncryptedData(result);
      toast.success('Data encrypted successfully');
      
      // Notify parent component
      if (onEncryptionComplete) {
        onEncryptionComplete(result);
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Placeholder for homomorphic encryption
  // In a real application, this would use a proper homomorphic encryption library
  const encryptHomomorphic = (dataPoints, params) => {
    // Simulate homomorphic encryption
    const publicKey = params.public_key;
    
    return {
      encryption_type: 'homomorphic',
      algorithm: 'paillier',
      encrypted_values: dataPoints.map(value => ({
        // This is a placeholder. In a real app, we would use actual homomorphic encryption
        value: value * 1000, // Simulated encryption
        n: publicKey.n,
        g: publicKey.g
      }))
    };
  };

  // Placeholder for hybrid encryption (homomorphic + SMPC)
  const encryptHybrid = (dataPoints, params) => {
    // Simulate homomorphic encryption
    const homomorphicKey = params.homomorphic.public_key;
    
    // Simulate SMPC shares generation
    const smpcParams = params.smpc;
    
    return {
      encryption_type: 'hybrid',
      homomorphic: {
        encrypted_values: dataPoints.map(value => ({
          // This is a placeholder. In a real app, we would use actual homomorphic encryption
          value: value * 1000, // Simulated encryption
          n: homomorphicKey.n,
          g: homomorphicKey.g
        }))
      },
      smpc_shares: {
        // This is a placeholder. In a real app, we would generate actual SMPC shares
        shares: generateSimulatedShares(dataPoints, smpcParams),
        threshold: smpcParams.threshold,
        total_shares: smpcParams.total_shares,
        prime: smpcParams.prime
      }
    };
  };

  // Placeholder for SMPC shares generation
  const generateSimulatedShares = (dataPoints, params) => {
    const shares = {};
    
    // For each participant, generate a "share" (this is just a simulation)
    params.participant_ids.forEach((participantId, index) => {
      shares[participantId] = dataPoints.map(value => {
        return {
          x: index + 1,
          y: (value * (index + 1)) % parseInt(params.prime)
        };
      });
    });
    
    return shares;
  };

  return (
    <div className="bg-white shadow sm:rounded-lg p-6 mt-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Secure Client-Side Encryption</h3>
      
      {!encryptionParams ? (
        <div>
          <p className="text-sm text-gray-500 mb-4">
            Fetch encryption parameters to securely encrypt your data before submission.
          </p>
          <button
            onClick={fetchEncryptionParams}
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Fetching...' : 'Fetch Encryption Parameters'}
          </button>
        </div>
      ) : (
        <div>
          <div className="mb-4">
            <p className="text-sm text-gray-500 mb-2">
              Encryption Type: <span className="font-semibold">{encryptionParams.encryption_type}</span>
            </p>
            {encryptionParams.encryption_type === 'homomorphic' && (
              <p className="text-sm text-gray-500">
                Algorithm: <span className="font-semibold">{encryptionParams.algorithm}</span>
              </p>
            )}
            {encryptionParams.encryption_type === 'hybrid' && (
              <div>
                <p className="text-sm text-gray-500">
                  Homomorphic Algorithm: <span className="font-semibold">{encryptionParams.homomorphic.algorithm}</span>
                </p>
                <p className="text-sm text-gray-500">
                  SMPC Algorithm: <span className="font-semibold">{encryptionParams.smpc.algorithm}</span>
                </p>
                <p className="text-sm text-gray-500">
                  Threshold: <span className="font-semibold">{encryptionParams.smpc.threshold}</span>
                </p>
              </div>
            )}
          </div>
          
          <div className="mb-4">
            <label htmlFor="dataToEncrypt" className="block text-sm font-medium text-gray-700 mb-1">
              Enter Data (comma-separated numbers)
            </label>
            <textarea
              id="dataToEncrypt"
              value={dataToEncrypt}
              onChange={(e) => setDataToEncrypt(e.target.value)}
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              rows="3"
              placeholder="e.g., 45.2, 67.8, 32.1"
            />
          </div>
          
          <button
            onClick={encryptData}
            disabled={isLoading || !dataToEncrypt}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {isLoading ? 'Encrypting...' : 'Encrypt Data'}
          </button>
          
          {encryptedData && (
            <div className="mt-4">
              <h4 className="text-md font-medium text-gray-900 mb-2">Encrypted Data</h4>
              <div className="bg-gray-50 p-3 rounded-md">
                <pre className="text-xs overflow-auto max-h-40">
                  {JSON.stringify(encryptedData, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SecureEncryption;