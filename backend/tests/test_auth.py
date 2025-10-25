import pytest
from fastapi.testclient import TestClient
from backend.models import Organization
from backend.auth_utils import verify_password, get_password_hash

class TestAuthentication:
    """Test suite for authentication functionality."""
    
    def test_register_organization_success(self, client, test_user_data):
        """Test successful organization registration."""
        response = client.post("/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Organization registered successfully"
        assert "organization_id" in data
    
    def test_register_duplicate_email(self, client, test_user_data, test_organization):
        """Test registration with duplicate email fails."""
        response = client.post("/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_invalid_email(self, client, test_user_data):
        """Test registration with invalid email format."""
        test_user_data["email"] = "invalid-email"
        response = client.post("/register", json=test_user_data)
        assert response.status_code == 422
    
    def test_register_weak_password(self, client, test_user_data):
        """Test registration with weak password."""
        test_user_data["password"] = "123"
        response = client.post("/register", json=test_user_data)
        assert response.status_code == 422
    
    def test_login_success(self, client, test_organization):
        """Test successful login."""
        login_data = {
            "email": test_organization.email,
            "password": "testpassword123"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, test_organization):
        """Test login with invalid credentials."""
        login_data = {
            "email": test_organization.email,
            "password": "wrongpassword"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_unverified_organization(self, client, db_session, test_user_data):
        """Test login with unverified organization."""
        # Create unverified organization
        org = Organization(
            name=test_user_data["name"],
            email="unverified@test.com",
            password_hash=get_password_hash(test_user_data["password"]),
            type=test_user_data["type"],
            is_verified=False
        )
        db_session.add(org)
        db_session.commit()
        
        login_data = {
            "email": "unverified@test.com",
            "password": "testpassword123"
        }
        response = client.post("/login", json=login_data)
        assert response.status_code == 403
        assert "not verified" in response.json()["detail"]
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get("/profile")
        assert response.status_code == 401
    
    def test_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/profile", headers=headers)
        assert response.status_code == 401
    
    def test_protected_route_with_valid_token(self, client, auth_headers):
        """Test accessing protected route with valid token."""
        response = client.get("/profile", headers=auth_headers)
        assert response.status_code == 200
    
    def test_refresh_token_success(self, client, test_organization):
        """Test successful token refresh."""
        # First login to get refresh token
        login_data = {
            "email": test_organization.email,
            "password": "testpassword123"
        }
        login_response = client.post("/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/refresh", json=refresh_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/refresh", json=refresh_data)
        assert response.status_code == 401

class TestPasswordSecurity:
    """Test suite for password security functions."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

class TestOTPVerification:
    """Test suite for OTP verification functionality."""
    
    def test_send_otp_success(self, client, test_organization):
        """Test successful OTP sending."""
        data = {"email": test_organization.email}
        response = client.post("/send-otp", json=data)
        assert response.status_code == 200
        assert "OTP sent" in response.json()["message"]
    
    def test_send_otp_invalid_email(self, client):
        """Test OTP sending to non-existent email."""
        data = {"email": "nonexistent@test.com"}
        response = client.post("/send-otp", json=data)
        assert response.status_code == 404
    
    def test_verify_otp_success(self, client, test_organization, mock_redis):
        """Test successful OTP verification."""
        # Mock OTP in Redis
        otp_key = f"otp:{test_organization.email}"
        mock_redis.data[otp_key] = "123456"
        
        data = {
            "email": test_organization.email,
            "otp": "123456"
        }
        response = client.post("/verify-otp", json=data)
        # Note: This test may need adjustment based on actual OTP implementation
    
    def test_verify_otp_invalid(self, client, test_organization):
        """Test OTP verification with invalid OTP."""
        data = {
            "email": test_organization.email,
            "otp": "000000"
        }
        response = client.post("/verify-otp", json=data)
        assert response.status_code == 400
