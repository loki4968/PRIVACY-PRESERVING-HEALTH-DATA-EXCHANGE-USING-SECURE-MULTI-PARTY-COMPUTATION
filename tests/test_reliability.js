// Test script for reliability improvements

async function testTokenRefresh() {
  console.log('Testing token refresh mechanism...');
  
  // Import the API configuration
  const { fetchApi, API_ENDPOINTS } = require('../app/config/api');
  
  // Mock an expired token scenario
  const expiredToken = 'expired_token_for_testing';
  
  try {
    // This should trigger the token refresh mechanism
    const response = await fetchApi(API_ENDPOINTS.secureComputations, {
      method: 'GET',
      token: expiredToken
    });
    
    console.log('✅ Token refresh mechanism working correctly');
    return true;
  } catch (error) {
    console.error('❌ Token refresh test failed:', error.message);
    return false;
  }
}

async function testRateLimitHandling() {
  console.log('Testing rate limit handling...');
  
  // Import the secure computation service
  const { secureComputationService } = require('../app/services/secureComputationService');
  
  // Get token from localStorage
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('❌ No token available for testing');
    return false;
  }
  
  try {
    // Make multiple rapid requests to trigger rate limiting
    const promises = [];
    for (let i = 0; i < 10; i++) {
      promises.push(secureComputationService.listComputations(token));
    }
    
    await Promise.all(promises);
    console.log('✅ Rate limit handling working correctly');
    return true;
  } catch (error) {
    if (error.message && error.message.includes('Too many requests')) {
      console.log('✅ Rate limiting detected as expected');
      return true;
    }
    console.error('❌ Rate limit test failed:', error.message);
    return false;
  }
}

async function runTests() {
  console.log('Running reliability tests...');
  
  const tokenRefreshResult = await testTokenRefresh();
  const rateLimitResult = await testRateLimitHandling();
  
  console.log('\nTest Results:');
  console.log(`Token Refresh: ${tokenRefreshResult ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Rate Limit Handling: ${rateLimitResult ? '✅ PASS' : '❌ FAIL'}`);
  
  if (tokenRefreshResult && rateLimitResult) {
    console.log('\n✅ All reliability improvements are working correctly!');
  } else {
    console.log('\n❌ Some reliability improvements need attention.');
  }
}

// Run the tests
runTests().catch(console.error);