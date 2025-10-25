import pytest
import numpy as np
from backend.smpc_protocols import ShamirSecretSharing, SMPCProtocol
from backend.secure_computation import SecureComputationService
from backend.models import SecureComputation, ComputationParticipant

class TestShamirSecretSharing:
    """Test suite for Shamir's Secret Sharing implementation."""
    
    def test_secret_sharing_basic(self):
        """Test basic secret sharing and reconstruction."""
        sss = ShamirSecretSharing(threshold=3, num_shares=5)
        secret = 12345
        
        shares = sss.generate_shares(secret)
        assert len(shares) == 5
        
        # Test reconstruction with minimum shares
        reconstructed = sss.reconstruct_secret(shares[:3])
        assert reconstructed == secret
        
        # Test reconstruction with more than minimum shares
        reconstructed = sss.reconstruct_secret(shares[:4])
        assert reconstructed == secret
    
    def test_insufficient_shares(self):
        """Test that reconstruction fails with insufficient shares."""
        sss = ShamirSecretSharing(threshold=3, num_shares=5)
        secret = 12345
        
        shares = sss.generate_shares(secret)
        
        # Should fail with less than threshold shares
        with pytest.raises(ValueError):
            sss.reconstruct_secret(shares[:2])
    
    def test_large_numbers(self):
        """Test secret sharing with large numbers."""
        sss = ShamirSecretSharing(threshold=2, num_shares=3)
        secret = 999999999999999
        
        shares = sss.generate_shares(secret)
        reconstructed = sss.reconstruct_secret(shares[:2])
        assert reconstructed == secret
    
    def test_negative_numbers(self):
        """Test secret sharing with negative numbers."""
        sss = ShamirSecretSharing(threshold=2, num_shares=3)
        secret = -12345
        
        shares = sss.generate_shares(secret)
        reconstructed = sss.reconstruct_secret(shares[:2])
        assert reconstructed == secret

class TestSMPCProtocol:
    """Test suite for SMPC Protocol implementation."""
    
    def test_secure_sum(self):
        """Test secure sum computation."""
        protocol = SMPCProtocol(threshold=2, num_parties=3)
        
        # Test data from different parties
        party1_data = [10, 20, 30]
        party2_data = [15, 25, 35]
        party3_data = [5, 15, 25]
        
        # Generate shares for each party
        shares1 = protocol.generate_data_shares(party1_data)
        shares2 = protocol.generate_data_shares(party2_data)
        shares3 = protocol.generate_data_shares(party3_data)
        
        # Combine shares from all parties
        all_shares = [shares1, shares2, shares3]
        
        # Compute secure sum
        result = protocol.secure_sum(all_shares)
        expected_sum = sum(party1_data) + sum(party2_data) + sum(party3_data)
        
        assert abs(result - expected_sum) < 0.001  # Allow for floating point errors
    
    def test_secure_mean(self):
        """Test secure mean computation."""
        protocol = SMPCProtocol(threshold=2, num_parties=2)
        
        party1_data = [100, 200, 300]
        party2_data = [150, 250, 350]
        
        shares1 = protocol.generate_data_shares(party1_data)
        shares2 = protocol.generate_data_shares(party2_data)
        
        all_shares = [shares1, shares2]
        result = protocol.secure_mean(all_shares)
        
        all_data = party1_data + party2_data
        expected_mean = sum(all_data) / len(all_data)
        
        assert abs(result - expected_mean) < 0.001
    
    def test_secure_variance(self):
        """Test secure variance computation."""
        protocol = SMPCProtocol(threshold=2, num_parties=2)
        
        party1_data = [1, 2, 3, 4, 5]
        party2_data = [6, 7, 8, 9, 10]
        
        shares1 = protocol.generate_data_shares(party1_data)
        shares2 = protocol.generate_data_shares(party2_data)
        
        all_shares = [shares1, shares2]
        result = protocol.secure_variance(all_shares)
        
        # Calculate expected variance
        all_data = party1_data + party2_data
        mean = sum(all_data) / len(all_data)
        expected_variance = sum((x - mean) ** 2 for x in all_data) / len(all_data)
        
        assert abs(result - expected_variance) < 0.001
    
    def test_secure_correlation(self):
        """Test secure correlation computation."""
        protocol = SMPCProtocol(threshold=2, num_parties=2)
        
        # Create correlated data
        x_data = [1, 2, 3, 4, 5]
        y_data = [2, 4, 6, 8, 10]  # Perfect positive correlation
        
        x_shares = protocol.generate_data_shares(x_data)
        y_shares = protocol.generate_data_shares(y_data)
        
        correlation = protocol.secure_correlation([x_shares], [y_shares])
        
        # Should be close to 1.0 for perfect positive correlation
        assert abs(correlation - 1.0) < 0.001
    
    def test_empty_data(self):
        """Test protocol behavior with empty data."""
        protocol = SMPCProtocol(threshold=2, num_parties=2)
        
        with pytest.raises((ValueError, ZeroDivisionError)):
            protocol.generate_data_shares([])

class TestSecureComputationService:
    """Test suite for Secure Computation Service."""
    
    @pytest.fixture
    def computation_service(self, db_session):
        """Create a computation service instance."""
        return SecureComputationService(db_session)
    
    def test_create_computation(self, computation_service, test_organization, sample_computation_request):
        """Test creating a new secure computation."""
        computation = computation_service.create_computation(
            creator_id=test_organization.id,
            **sample_computation_request
        )
        
        assert computation.title == sample_computation_request["title"]
        assert computation.creator_id == test_organization.id
        assert computation.status == "PENDING"
    
    def test_join_computation(self, computation_service, test_organization, sample_computation_request, db_session):
        """Test joining an existing computation."""
        # Create computation
        computation = computation_service.create_computation(
            creator_id=test_organization.id,
            **sample_computation_request
        )
        
        # Create another organization to join
        from backend.models import Organization
        from backend.auth_utils import get_password_hash
        
        org2 = Organization(
            name="Test Clinic",
            email="clinic@test.com",
            password_hash=get_password_hash("password123"),
            type="clinic",
            is_verified=True
        )
        db_session.add(org2)
        db_session.commit()
        db_session.refresh(org2)
        
        # Join computation
        success = computation_service.join_computation(
            computation_id=computation.computation_id,
            participant_id=org2.id
        )
        
        assert success
        
        # Verify participant was added
        participant = db_session.query(ComputationParticipant).filter(
            ComputationParticipant.computation_id == computation.computation_id,
            ComputationParticipant.organization_id == org2.id
        ).first()
        
        assert participant is not None
    
    def test_submit_data(self, computation_service, test_organization, sample_computation_request, sample_health_metrics):
        """Test submitting data to a computation."""
        # Create computation
        computation = computation_service.create_computation(
            creator_id=test_organization.id,
            **sample_computation_request
        )
        
        # Submit data
        success = computation_service.submit_data(
            computation_id=computation.computation_id,
            participant_id=test_organization.id,
            data=sample_health_metrics
        )
        
        assert success
    
    def test_execute_computation_statistics(self, computation_service, test_organization, sample_health_metrics, db_session):
        """Test executing a statistical computation."""
        # Create computation request for statistics
        request = {
            "title": "Blood Pressure Statistics",
            "description": "Calculate blood pressure statistics",
            "computation_type": "statistics",
            "participants": [test_organization.email],
            "parameters": {
                "metrics": ["blood_pressure"],
                "operations": ["mean", "std", "count"]
            }
        }
        
        computation = computation_service.create_computation(
            creator_id=test_organization.id,
            **request
        )
        
        # Submit data
        computation_service.submit_data(
            computation_id=computation.computation_id,
            participant_id=test_organization.id,
            data={"blood_pressure": sample_health_metrics["blood_pressure"]}
        )
        
        # Execute computation
        result = computation_service.execute_computation(computation.computation_id)
        
        assert result is not None
        assert "blood_pressure" in result
        assert "mean" in result["blood_pressure"]
        assert "std" in result["blood_pressure"]
        assert "count" in result["blood_pressure"]
    
    def test_get_computation_results(self, computation_service, test_organization, sample_computation_request):
        """Test retrieving computation results."""
        # Create and execute computation
        computation = computation_service.create_computation(
            creator_id=test_organization.id,
            **sample_computation_request
        )
        
        # Get results (should be empty initially)
        results = computation_service.get_computation_results(computation.computation_id)
        assert results == []
    
    def test_invalid_computation_id(self, computation_service):
        """Test operations with invalid computation ID."""
        invalid_id = "invalid-computation-id"
        
        # Should return None or raise appropriate exception
        result = computation_service.get_computation_results(invalid_id)
        assert result is None or result == []
    
    def test_duplicate_data_submission(self, computation_service, test_organization, sample_computation_request, sample_health_metrics):
        """Test submitting data multiple times from same participant."""
        computation = computation_service.create_computation(
            creator_id=test_organization.id,
            **sample_computation_request
        )
        
        # First submission
        success1 = computation_service.submit_data(
            computation_id=computation.computation_id,
            participant_id=test_organization.id,
            data=sample_health_metrics
        )
        
        # Second submission (should handle gracefully)
        success2 = computation_service.submit_data(
            computation_id=computation.computation_id,
            participant_id=test_organization.id,
            data=sample_health_metrics
        )
        
        assert success1
        # Second submission behavior depends on implementation
        # Could be True (update) or False (reject duplicate)

class TestSMPCIntegration:
    """Integration tests for SMPC functionality."""
    
    def test_end_to_end_secure_computation(self, db_session):
        """Test complete end-to-end secure computation workflow."""
        from backend.models import Organization
        from backend.auth_utils import get_password_hash
        
        # Create multiple organizations
        orgs = []
        for i in range(3):
            org = Organization(
                name=f"Hospital {i+1}",
                email=f"hospital{i+1}@test.com",
                password_hash=get_password_hash("password123"),
                type="hospital",
                is_verified=True
            )
            db_session.add(org)
            orgs.append(org)
        
        db_session.commit()
        for org in orgs:
            db_session.refresh(org)
        
        # Create computation service
        service = SecureComputationService(db_session)
        
        # Create computation
        computation = service.create_computation(
            creator_id=orgs[0].id,
            title="Multi-Party Blood Pressure Analysis",
            description="Secure analysis across multiple hospitals",
            computation_type="statistics",
            participants=[org.email for org in orgs],
            parameters={
                "metrics": ["blood_pressure_systolic"],
                "operations": ["mean", "count"]
            }
        )
        
        # All organizations join
        for org in orgs[1:]:
            service.join_computation(computation.computation_id, org.id)
        
        # Each organization submits data
        test_data = [
            {"blood_pressure_systolic": [120, 130, 125]},
            {"blood_pressure_systolic": [135, 140, 132]},
            {"blood_pressure_systolic": [115, 118, 122]}
        ]
        
        for i, org in enumerate(orgs):
            service.submit_data(
                computation.computation_id,
                org.id,
                test_data[i]
            )
        
        # Execute computation
        result = service.execute_computation(computation.computation_id)
        
        # Verify results
        assert result is not None
        assert "blood_pressure_systolic" in result
        
        # Calculate expected values
        all_values = []
        for data in test_data:
            all_values.extend(data["blood_pressure_systolic"])
        
        expected_mean = sum(all_values) / len(all_values)
        expected_count = len(all_values)
        
        assert abs(result["blood_pressure_systolic"]["mean"] - expected_mean) < 0.001
        assert result["blood_pressure_systolic"]["count"] == expected_count
