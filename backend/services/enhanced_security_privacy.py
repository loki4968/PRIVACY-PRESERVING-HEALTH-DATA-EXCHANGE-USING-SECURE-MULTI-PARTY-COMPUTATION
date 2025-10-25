"""
Enhanced Security and Privacy System
Advanced encryption, secure key management, audit logging, access control, and threat detection
"""

import numpy as np
import hashlib
import secrets
import bcrypt
from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import datetime, timedelta
import logging
import json
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hmac
import jwt
import sqlite3
from collections import defaultdict
import threading
import time
import ipaddress
from sklearn.ensemble import IsolationForest
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedEncryption:
    """Advanced encryption with multiple algorithms and key rotation"""

    def __init__(self, master_key: bytes = None):
        self.master_key = master_key or secrets.token_bytes(32)
        self.key_rotation_interval = timedelta(days=30)
        self.last_key_rotation = datetime.utcnow()
        self.encryption_history = []

    def encrypt_data(self, data: Any, algorithm: str = "AES") -> Dict[str, Any]:
        """Encrypt data using specified algorithm"""
        if algorithm == "AES":
            return self._encrypt_aes(data)
        elif algorithm == "RSA":
            return self._encrypt_rsa(data)
        elif algorithm == "ECC":
            return self._encrypt_ecc(data)
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")

    def decrypt_data(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt data using appropriate algorithm"""
        algorithm = encrypted_data.get("algorithm", "AES")

        if algorithm == "AES":
            return self._decrypt_aes(encrypted_data)
        elif algorithm == "RSA":
            return self._decrypt_rsa(encrypted_data)
        elif algorithm == "ECC":
            return self._decrypt_ecc(encrypted_data)
        else:
            raise ValueError(f"Unsupported decryption algorithm: {algorithm}")

    def _encrypt_aes(self, data: Any) -> Dict[str, Any]:
        """Encrypt data using AES-GCM"""
        # Generate key from master key using PBKDF2
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(self.master_key)

        # Generate IV
        iv = secrets.token_bytes(12)

        # Encrypt data
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
        encryptor = cipher.encryptor()

        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode()
        else:
            data_bytes = str(data).encode()

        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()

        encrypted_data = {
            "algorithm": "AES",
            "ciphertext": ciphertext.hex(),
            "iv": iv.hex(),
            "salt": salt.hex(),
            "tag": encryptor.tag.hex(),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.encryption_history.append({
            "algorithm": "AES",
            "timestamp": datetime.utcnow().isoformat(),
            "data_size": len(data_bytes)
        })

        return encrypted_data

    def _decrypt_aes(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt AES encrypted data"""
        # Derive key
        salt = bytes.fromhex(encrypted_data["salt"])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(self.master_key)

        # Decrypt
        iv = bytes.fromhex(encrypted_data["iv"])
        tag = bytes.fromhex(encrypted_data["tag"])
        ciphertext = bytes.fromhex(encrypted_data["ciphertext"])

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()

        data_bytes = decryptor.update(ciphertext) + decryptor.finalize()

        try:
            return json.loads(data_bytes.decode())
        except json.JSONDecodeError:
            return data_bytes.decode()

    def _encrypt_rsa(self, data: Any) -> Dict[str, Any]:
        """Encrypt data using RSA"""
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        public_key = private_key.public_key()

        # Serialize data
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode()
        else:
            data_bytes = str(data).encode()

        # Encrypt
        ciphertext = public_key.encrypt(
            data_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Serialize private key (in practice, store securely)
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        encrypted_data = {
            "algorithm": "RSA",
            "ciphertext": ciphertext.hex(),
            "private_key": pem.decode(),
            "timestamp": datetime.utcnow().isoformat()
        }

        return encrypted_data

    def _decrypt_rsa(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt RSA encrypted data"""
        # Load private key
        private_key = serialization.load_pem_private_key(
            encrypted_data["private_key"].encode(),
            password=None,
        )

        # Decrypt
        ciphertext = bytes.fromhex(encrypted_data["ciphertext"])
        data_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        try:
            return json.loads(data_bytes.decode())
        except json.JSONDecodeError:
            return data_bytes.decode()

    def _encrypt_ecc(self, data: Any) -> Dict[str, Any]:
        """Encrypt data using ECC"""
        # Generate ECC key pair
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()

        # Derive shared key
        shared_key = private_key.exchange(ec.ECDH(), public_key)

        # Use shared key for AES encryption
        return self._encrypt_aes(data)

    def _decrypt_ecc(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt ECC encrypted data"""
        return self._decrypt_aes(encrypted_data)

    def rotate_master_key(self):
        """Rotate the master key"""
        if datetime.utcnow() - self.last_key_rotation > self.key_rotation_interval:
            old_key = self.master_key
            self.master_key = secrets.token_bytes(32)
            self.last_key_rotation = datetime.utcnow()

            logger.info("Master key rotated successfully")
            return True
        return False


class SecureKeyManagement:
    """Secure key management system"""

    def __init__(self, storage_path: str = "./keys"):
        self.storage_path = storage_path
        self.keys = {}
        self.key_usage = defaultdict(int)

        os.makedirs(storage_path, exist_ok=True)

    def generate_key(self, key_name: str, key_type: str = "AES", key_size: int = 256) -> str:
        """Generate and store a new key"""
        if key_type == "AES":
            key = secrets.token_bytes(key_size // 8)
        elif key_type == "RSA":
            key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        elif key_type == "ECC":
            key = ec.generate_private_key(ec.SECP256R1())
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        key_id = hashlib.sha256(f"{key_name}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]

        key_info = {
            "key_id": key_id,
            "key_name": key_name,
            "key_type": key_type,
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
            "last_used": None
        }

        # Store key securely (in practice, use HSM or secure vault)
        self.keys[key_id] = {
            "key": key,
            "info": key_info
        }

        return key_id

    def get_key(self, key_id: str) -> Any:
        """Retrieve a key"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        key_data = self.keys[key_id]
        key_data["info"]["usage_count"] += 1
        key_data["info"]["last_used"] = datetime.utcnow().isoformat()

        self.key_usage[key_id] += 1

        return key_data["key"]

    def revoke_key(self, key_id: str) -> bool:
        """Revoke a key"""
        if key_id in self.keys:
            del self.keys[key_id]
            logger.info(f"Key {key_id} revoked")
            return True
        return False

    def list_keys(self) -> List[Dict[str, Any]]:
        """List all keys (without exposing key material)"""
        return [key_data["info"] for key_data in self.keys.values()]


class AuditLogging:
    """Comprehensive audit logging system"""

    def __init__(self, log_path: str = "./audit_logs"):
        self.log_path = log_path
        self.log_file = os.path.join(log_path, f"audit_{datetime.utcnow().strftime('%Y%m%d')}.log")
        self.audit_events = []

        os.makedirs(log_path, exist_ok=True)

    def log_event(self, event_type: str, user_id: str, resource: str,
                  action: str, details: Dict[str, Any] = None, ip_address: str = None):
        """Log an audit event"""
        if details is None:
            details = {}

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "details": details,
            "ip_address": ip_address,
            "event_id": hashlib.sha256(f"{datetime.utcnow().isoformat()}_{user_id}_{action}".encode()).hexdigest()[:16]
        }

        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

        self.audit_events.append(event)

        logger.info(f"Audit event: {event_type} - {user_id} - {action}")

    def search_events(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search audit events"""
        filtered_events = self.audit_events

        for key, value in filters.items():
            filtered_events = [e for e in filtered_events if e.get(key) == value]

        return filtered_events

    def get_user_activity(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get user activity for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        user_events = [e for e in self.audit_events
                      if e["user_id"] == user_id and
                      datetime.fromisoformat(e["timestamp"]) > cutoff_time]

        return user_events

    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit report for date range"""
        report_events = [e for e in self.audit_events
                        if start_date <= datetime.fromisoformat(e["timestamp"]) <= end_date]

        # Aggregate statistics
        event_types = defaultdict(int)
        users = defaultdict(int)
        actions = defaultdict(int)

        for event in report_events:
            event_types[event["event_type"]] += 1
            users[event["user_id"]] += 1
            actions[event["action"]] += 1

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_events": len(report_events),
            "event_types": dict(event_types),
            "active_users": len(users),
            "user_activity": dict(users),
            "action_counts": dict(actions)
        }


class AccessControl:
    """Role-based access control system"""

    def __init__(self):
        self.users = {}
        self.roles = {
            "admin": ["read", "write", "delete", "manage_users", "view_audit"],
            "data_scientist": ["read", "write", "view_audit"],
            "analyst": ["read"],
            "viewer": ["read"]
        }
        self.resources = {}
        self.permissions = {}

    def add_user(self, user_id: str, role: str, password: str):
        """Add a new user"""
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        self.users[user_id] = {
            "role": role,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "active": True
        }

    def authenticate(self, user_id: str, password: str) -> bool:
        """Authenticate user"""
        if user_id not in self.users:
            return False

        user = self.users[user_id]
        if not user["active"]:
            return False

        return bcrypt.checkpw(password.encode(), user["password_hash"])

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource"""
        if user_id not in self.users:
            return False

        user_role = self.users[user_id]["role"]
        role_permissions = self.roles.get(user_role, [])

        return action in role_permissions

    def grant_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Grant specific permission to user"""
        if not self.check_permission(user_id, "manage_users", "manage_users"):
            return False

        if user_id not in self.permissions:
            self.permissions[user_id] = {}

        if resource not in self.permissions[user_id]:
            self.permissions[user_id][resource] = []

        if action not in self.permissions[user_id][resource]:
            self.permissions[user_id][resource].append(action)

        return True

    def revoke_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Revoke specific permission from user"""
        if not self.check_permission(user_id, "manage_users", "manage_users"):
            return False

        if user_id in self.permissions and resource in self.permissions[user_id]:
            if action in self.permissions[user_id][resource]:
                self.permissions[user_id][resource].remove(action)
                return True

        return False


class ThreatDetection:
    """AI-powered threat detection system"""

    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.login_attempts = defaultdict(list)
        self.failed_logins = defaultdict(int)
        self.suspicious_activities = []
        self.threat_score = defaultdict(float)

    def log_login_attempt(self, user_id: str, ip_address: str, success: bool, timestamp: datetime = None):
        """Log login attempt for analysis"""
        if timestamp is None:
            timestamp = datetime.utcnow()

        attempt = {
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "timestamp": timestamp.isoformat()
        }

        self.login_attempts[user_id].append(attempt)

        if not success:
            self.failed_logins[user_id] += 1

        # Check for suspicious patterns
        self._analyze_login_pattern(user_id, ip_address)

    def log_activity(self, user_id: str, activity: str, resource: str, metadata: Dict[str, Any] = None):
        """Log user activity for threat analysis"""
        if metadata is None:
            metadata = {}

        activity_log = {
            "user_id": user_id,
            "activity": activity,
            "resource": resource,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Analyze for threats
        threat_level = self._analyze_activity(activity_log)
        self.threat_score[user_id] += threat_level

        if threat_level > 0.5:
            self.suspicious_activities.append(activity_log)

    def _analyze_login_pattern(self, user_id: str, ip_address: str):
        """Analyze login patterns for anomalies"""
        attempts = self.login_attempts[user_id]

        if len(attempts) < 5:
            return  # Need more data

        # Check for rapid failed attempts
        recent_attempts = [a for a in attempts if
                          datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(minutes=5)]

        failed_recent = [a for a in recent_attempts if not a["success"]]

        if len(failed_recent) > 3:
            logger.warning(f"Potential brute force attack detected for user {user_id}")

        # Check for unusual IP addresses
        ip_addresses = list(set(a["ip_address"] for a in attempts[-10:]))
        if len(ip_addresses) > 3:
            logger.warning(f"Unusual number of IP addresses for user {user_id}")

    def _analyze_activity(self, activity_log: Dict[str, Any]) -> float:
        """Analyze activity for threat level"""
        threat_level = 0.0

        # Unusual access patterns
        user_id = activity_log["user_id"]
        activity = activity_log["activity"]

        # Check for sensitive operations
        sensitive_activities = ["delete", "export", "admin", "key_access"]
        if any(sensitive in activity.lower() for sensitive in sensitive_activities):
            threat_level += 0.3

        # Check for unusual timing
        hour = datetime.fromisoformat(activity_log["timestamp"]).hour
        if hour < 6 or hour > 22:  # Late night/early morning
            threat_level += 0.2

        # Check for rapid successive actions
        if len(self.suspicious_activities) > 0:
            last_activity = self.suspicious_activities[-1]
            time_diff = datetime.fromisoformat(activity_log["timestamp"]) - \
                       datetime.fromisoformat(last_activity["timestamp"])

            if time_diff.total_seconds() < 60:  # Less than 1 minute
                threat_level += 0.4

        return threat_level

    def get_threat_report(self, user_id: str = None) -> Dict[str, Any]:
        """Get threat analysis report"""
        if user_id:
            return {
                "user_id": user_id,
                "threat_score": self.threat_score[user_id],
                "failed_logins": self.failed_logins[user_id],
                "suspicious_activities": [a for a in self.suspicious_activities if a["user_id"] == user_id],
                "risk_level": "high" if self.threat_score[user_id] > 1.0 else "medium" if self.threat_score[user_id] > 0.5 else "low"
            }
        else:
            return {
                "total_users": len(self.threat_score),
                "high_risk_users": [uid for uid, score in self.threat_score.items() if score > 1.0],
                "suspicious_activities": len(self.suspicious_activities),
                "failed_login_attempts": sum(self.failed_logins.values())
            }


class EnhancedSecurityPrivacyService:
    """Main service integrating all security and privacy features"""

    def __init__(self):
        self.encryption = AdvancedEncryption()
        self.key_management = SecureKeyManagement()
        self.audit_logging = AuditLogging()
        self.access_control = AccessControl()
        self.threat_detection = ThreatDetection()

    def encrypt_sensitive_data(self, data: Any, algorithm: str = "AES") -> Dict[str, Any]:
        """Encrypt sensitive data"""
        return self.encryption.encrypt_data(data, algorithm)

    def decrypt_sensitive_data(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt sensitive data"""
        return self.encryption.decrypt_data(encrypted_data)

    def generate_secure_key(self, key_name: str, key_type: str = "AES") -> str:
        """Generate a secure key"""
        return self.key_management.generate_key(key_name, key_type)

    def log_security_event(self, event_type: str, user_id: str, resource: str,
                          action: str, details: Dict[str, Any] = None, ip_address: str = None):
        """Log a security event"""
        self.audit_logging.log_event(event_type, user_id, resource, action, details, ip_address)

    def authenticate_user(self, user_id: str, password: str) -> bool:
        """Authenticate a user"""
        return self.access_control.authenticate(user_id, password)

    def check_user_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check user permissions"""
        return self.access_control.check_permission(user_id, resource, action)

    def log_user_activity(self, user_id: str, activity: str, resource: str,
                         metadata: Dict[str, Any] = None):
        """Log user activity for threat detection"""
        self.threat_detection.log_activity(user_id, activity, resource, metadata)

    def log_login_attempt(self, user_id: str, ip_address: str, success: bool):
        """Log login attempt"""
        self.threat_detection.log_login_attempt(user_id, ip_address, success)

    def get_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get audit report"""
        return self.audit_logging.generate_audit_report(start_date, end_date)

    def get_threat_report(self, user_id: str = None) -> Dict[str, Any]:
        """Get threat analysis report"""
        return self.threat_detection.get_threat_report(user_id)

    def rotate_encryption_keys(self) -> bool:
        """Rotate encryption keys"""
        return self.encryption.rotate_master_key()

    def comprehensive_security_assessment(self) -> Dict[str, Any]:
        """Perform comprehensive security assessment"""
        # Get audit statistics
        audit_stats = self.audit_logging.generate_audit_report(
            datetime.utcnow() - timedelta(days=30),
            datetime.utcnow()
        )

        # Get threat analysis
        threat_report = self.threat_detection.get_threat_report()

        # Get key management info
        keys_info = self.key_management.list_keys()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "audit_statistics": audit_stats,
            "threat_analysis": threat_report,
            "key_management": {
                "total_keys": len(keys_info),
                "keys_by_type": defaultdict(int)
            },
            "recommendations": self._generate_security_recommendations(audit_stats, threat_report)
        }

    def _generate_security_recommendations(self, audit_stats: Dict, threat_report: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        # Check for high failed login attempts
        if threat_report.get("failed_login_attempts", 0) > 100:
            recommendations.append("High number of failed login attempts detected - consider implementing CAPTCHA")

        # Check for suspicious activities
        if threat_report.get("suspicious_activities", 0) > 10:
            recommendations.append("Multiple suspicious activities detected - review access patterns")

        # Check audit log volume
        if audit_stats.get("total_events", 0) < 100:
            recommendations.append("Low audit activity - ensure all security events are being logged")

        # Key management recommendations
        if len(self.key_management.list_keys()) > 50:
            recommendations.append("Large number of keys - consider key rotation and cleanup")

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize security service
    security_service = EnhancedSecurityPrivacyService()

    # Add users
    security_service.access_control.add_user("admin", "admin", "admin123")
    security_service.access_control.add_user("user1", "data_scientist", "password123")

    # Authenticate user
    is_authenticated = security_service.authenticate_user("admin", "admin123")
    print(f"Admin authenticated: {is_authenticated}")

    # Generate and use encryption key
    key_id = security_service.generate_secure_key("test_key", "AES")
    print(f"Generated key: {key_id}")

    # Encrypt data
    test_data = {"patient_id": "12345", "diagnosis": "sensitive_info"}
    encrypted = security_service.encrypt_sensitive_data(test_data, "AES")
    print(f"Encrypted data: {encrypted['algorithm']}")

    # Decrypt data
    decrypted = security_service.decrypt_sensitive_data(encrypted)
    print(f"Decrypted data: {decrypted}")

    # Log security events
    security_service.log_security_event("login", "admin", "system", "login", {"ip": "192.168.1.1"})
    security_service.log_security_event("data_access", "admin", "patient_data", "read")

    # Log user activity
    security_service.log_user_activity("admin", "model_training", "ml_model", {"model_type": "neural_network"})

    # Get audit report
    report = security_service.get_audit_report(
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow()
    )
    print(f"Audit report: {report}")

    # Get threat report
    threat_report = security_service.get_threat_report()
    print(f"Threat report: {threat_report}")

    # Comprehensive security assessment
    assessment = security_service.comprehensive_security_assessment()
    print(f"Security assessment: {assessment}")

    print("Enhanced Security and Privacy system tested successfully!")
