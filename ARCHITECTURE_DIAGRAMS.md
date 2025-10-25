# Architecture Diagrams & Flow Charts
## Privacy Preserving Health Data Exchange Using Secure Multi-Party Computation

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              HEALTH DATA EXCHANGE PLATFORM                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   FRONTEND      │    │    BACKEND      │    │   DATABASE      │            │
│  │   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │            │
│  │                 │    │                 │    │                 │            │
│  │ • React         │    │ • Python 3.11   │    │ • SQLite        │            │
│  │ • TypeScript    │    │ • FastAPI       │    │ • SQLAlchemy    │            │
│  │ • Tailwind CSS  │    │ • SQLAlchemy    │    │ • Migrations    │            │
│  │ • WebSocket     │    │ • JWT Auth      │    │ • Encryption    │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           │                       │                       │                    │
│           ▼                       ▼                       ▼                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   SECURITY      │    │  COMPUTATION    │    │  FILE STORAGE   │            │
│  │   LAYER         │    │   ENGINE        │    │                 │            │
│  │                 │    │                 │    │                 │            │
│  │ • HE            │    │ • SMPC          │    │ • Uploads       │            │
│  │ • SMPC          │    │ • Analytics     │    │ • Health Data   │            │
│  │ • JWT           │    │ • ML            │    │ • Results       │            │
│  │ • RBAC          │    │ • Export        │    │ • Backups       │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SECURITY ARCHITECTURE LAYERS

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SECURITY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    LAYER 4: APPLICATION SECURITY                            │ │
│  │                                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ JWT Auth    │  │ Role-Based  │  │ Rate        │  │ Input       │        │ │
│  │  │ & Tokens    │  │ Access      │  │ Limiting    │  │ Validation  │        │ │
│  │  │             │  │ Control     │  │             │  │             │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    LAYER 3: DATA SECURITY                                   │ │
│  │                                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Homomorphic │  │ Secure      │  │ Shamir's    │  │ Threshold   │        │ │
│  │  │ Encryption  │  │ Multi-Party │  │ Secret      │  │ Cryptography│        │ │
│  │  │ (HE)        │  │ Computation │  │ Sharing     │  │             │        │ │
│  │  │             │  │ (SMPC)      │  │             │  │             │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    LAYER 2: TRANSPORT SECURITY                              │ │
│  │                                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ TLS/SSL     │  │ Secure      │  │ HTTP/2      │  │ CORS        │        │ │
│  │  │ Encryption  │  │ WebSocket   │  │ Headers     │  │ Protection  │        │ │
│  │  │             │  │ Connections │  │             │  │             │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    LAYER 1: INFRASTRUCTURE SECURITY                         │ │
│  │                                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Database    │  │ Audit       │  │ Error       │  │ Monitoring  │        │ │
│  │  │ Encryption  │  │ Logging     │  │ Handling    │  │ & Alerting  │        │ │
│  │  │ at Rest     │  │             │  │             │  │             │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. SECURE MULTI-PARTY COMPUTATION FLOW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        SECURE MULTI-PARTY COMPUTATION FLOW                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Hospital A  │    │ Hospital B  │    │ Hospital C  │    │ Hospital D  │      │
│  │   Data A    │    │   Data B    │    │   Data C    │    │   Data D    │      │
│  │ (Encrypted) │    │ (Encrypted) │    │ (Encrypted) │    │ (Encrypted) │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    SECURE COMPUTATION ENGINE                                │ │
│  │                                                                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │ │
│  │  │ Homomorphic     │  │ Shamir's Secret │  │ Threshold       │            │ │
│  │  │ Encryption      │  │ Sharing         │  │ Reconstruction  │            │ │
│  │  │                 │  │                 │  │                 │            │ │
│  │  │ • Encrypt Data  │  │ • Split Secrets │  │ • Reconstruct   │            │ │
│  │  │ • Add Encrypted │  │ • Distribute    │  │ • Verify        │            │ │
│  │  │ • Multiply      │  │ • Aggregate     │  │ • Validate      │            │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘            │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│         ┌─────────────────────────────────────────────────────────┐            │
│         │              COMPUTATION PHASES                        │            │
│         ├─────────────────────────────────────────────────────────┤            │
│         │ 1. INITIALIZATION: Create computation session          │            │
│         │ 2. PARTICIPATION: Organizations join session           │            │
│         │ 3. DATA SUBMISSION: Submit encrypted data points       │            │
│         │ 4. COMPUTATION: Perform secure aggregation             │            │
│         │ 5. VERIFICATION: Verify computation integrity          │            │
│         │ 6. RESULT DISTRIBUTION: Share aggregated results       │            │
│         └─────────────────────────────────────────────────────────┘            │
│                                                                                 │
│         ┌─────────────────────────────────────────────────────────┐            │
│         │              AGGREGATED RESULTS                        │            │
│         │                                                         │            │
│         │ • Statistical Summary (Mean, Median, Variance)         │            │
│         │ • No Individual Data Points Revealed                   │            │
│         │ • Encrypted Result Storage                             │            │
│         │ • Audit Trail Maintained                               │            │
│         └─────────────────────────────────────────────────────────┘            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. ROLE-BASED ACCESS CONTROL MATRIX

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ROLE-BASED ACCESS CONTROL MATRIX                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────────┐ │
│  │ Permission  │Hospital │ Clinic  │   Lab   │Pharmacy │ Patient │   Admin     │ │
│  ├─────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────────┤ │
│  │ Read Data   │    ✅   │    ✅   │    ✅   │    ✅   │    ✅   │     ✅      │ │
│  │ Write Data  │    ✅   │    ✅   │    ✅   │    ✅   │    ❌   │     ✅      │ │
│  │ Delete Data │    ✅   │    ❌   │    ❌   │    ❌   │    ❌   │     ✅      │ │
│  │ Analytics   │    ✅   │    ✅   │    ✅   │    ❌   │    ❌   │     ✅      │ │
│  │ SMPC Create │    ✅   │    ✅   │    ✅   │    ❌   │    ❌   │     ✅      │ │
│  │ SMPC Join   │    ✅   │    ✅   │    ✅   │    ✅   │    ❌   │     ✅      │ │
│  │ Export Data │    ✅   │    ✅   │    ✅   │    ❌   │    ❌   │     ✅      │ │
│  │ User Mgmt   │    ❌   │    ❌   │    ❌   │    ❌   │    ❌   │     ✅      │ │
│  │ System Config│   ❌   │    ❌   │    ❌   │    ❌   │    ❌   │     ✅      │ │
│  │ Audit Logs  │    ❌   │    ❌   │    ❌   │    ❌   │    ❌   │     ✅      │ │
│  └─────────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. SECURITY METHOD COMPARISON

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SECURITY METHOD COMPARISON                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┐ │
│  │ Security    │ Data        │ Performance │ Complexity  │ Use Case            │ │
│  │ Method      │ Privacy     │             │             │                     │ │
│  ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────────┤ │
│  │ Standard    │     Low     │    High     │    Low      │ Non-sensitive data  │ │
│  │             │             │             │             │ Quick processing    │ │
│  │             │             │             │             │ Basic compliance    │ │
│  ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────────┤ │
│  │ Homomorphic │    High     │    Low      │   High      │ Sensitive data      │ │
│  │ Encryption  │             │             │             │ Additive operations │ │
│  │             │             │             │             │ Privacy-critical    │ │
│  ├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────────┤ │
│  │ Hybrid      │   Very High │   Very Low  │  Very High  │ Maximum security    │ │
│  │ (HE+SMPC)   │             │             │             │ Multi-party trust   │ │
│  │             │             │             │             │ Research-grade      │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. COMPUTATION WORKFLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COMPUTATION WORKFLOW DIAGRAM                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐                                                           │
│  │   INITIATE      │                                                           │
│  │ COMPUTATION     │                                                           │
│  │                 │                                                           │
│  │ • Select Type   │                                                           │
│  │ • Choose Method │                                                           │
│  │ • Set Parameters│                                                           │
│  └─────────────────┘                                                           │
│           │                                                                     │
│           ▼                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   INVITE        │    │   JOIN          │    │   WAIT FOR      │            │
│  │ PARTICIPANTS    │───►│ COMPUTATION     │───►│ PARTICIPANTS    │            │
│  │                 │    │                 │    │                 │            │
│  │ • Send Invites  │    │ • Accept Invite │    │ • Monitor Status│            │
│  │ • Set Threshold │    │ • Verify Access │    │ • Track Progress│            │
│  │ • Define Roles  │    │ • Join Session  │    │ • Timeout Check │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           ▼                       ▼                       ▼                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   SUBMIT        │    │   ENCRYPT       │    │   VALIDATE      │            │
│  │ DATA POINTS     │    │ DATA            │    │ SUBMISSIONS     │            │
│  │                 │    │                 │    │                 │            │
│  │ • Upload Files  │    │ • HE Encryption │    │ • Check Format  │            │
│  │ • Enter Values  │    │ • SMPC Shares   │    │ • Verify Data   │            │
│  │ • Select Columns│    │ • Key Management│    │ • Sanitize Input│            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           ▼                       ▼                       ▼                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   PERFORM       │    │   VERIFY        │    │   DISTRIBUTE    │            │
│  │ COMPUTATION     │    │ RESULTS         │    │ RESULTS         │            │
│  │                 │    │                 │    │                 │            │
│  │ • SMPC Protocol │    │ • Integrity     │    │ • Encrypted     │            │
│  │ • HE Operations │    │ • Accuracy      │    │ • Access Control│            │
│  │ • Aggregation   │    │ • Consistency   │    │ • Audit Trail   │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           ▼                       ▼                       ▼                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   EXPORT        │    │   NOTIFY        │    │   ARCHIVE       │            │
│  │ RESULTS         │    │ PARTICIPANTS    │    │ COMPUTATION     │            │
│  │                 │    │                 │    │                 │            │
│  │ • JSON Format   │    │ • Email Alerts  │    │ • Store Metadata│            │
│  │ • CSV Format    │    │ • Dashboard     │    │ • Backup Data   │            │
│  │ • Encrypted     │    │ • WebSocket     │    │ • Cleanup       │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. PROJECT STATUS OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PROJECT STATUS OVERVIEW                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              COMPLETION STATUS                             │ │
│  │                                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Core        │  │ Security    │  │ Data        │  │ User        │        │ │
│  │  │ Infrastructure│ │ Implementation│ │ Management  │ │ Interface   │        │ │
│  │  │             │  │             │  │             │  │             │        │ │
│  │  │ ✅ 100%     │  │ ✅ 95%      │  │ ✅ 90%      │  │ ✅ 85%      │        │ │
│  │  │ Complete    │  │ Complete    │  │ Complete    │  │ Complete    │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  │                                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ API         │  │ Real-time   │  │ Advanced    │  │ Production  │        │ │
│  │  │ Endpoints   │  │ Collaboration│  │ Analytics   │  │ Deployment  │        │ │
│  │  │             │  │             │  │             │  │             │        │ │
│  │  │ ✅ 90%      │  │ 🔄 70%      │  │ 🔄 75%      │  │ ❌ 0%       │        │ │
│  │  │ Complete    │  │ In Progress │  │ In Progress │  │ Not Started │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              IMPLEMENTED FEATURES                           │ │
│  │                                                                             │ │
│  │  ✅ Secure Multi-Party Computation (SMPC)                                  │ │
│  │  ✅ Homomorphic Encryption (HE)                                            │ │
│  │  ✅ Role-Based Access Control (RBAC)                                       │ │
│  │  ✅ JWT Authentication & Authorization                                     │ │
│  │  ✅ Real-time Dashboard & Analytics                                        │ │
│  │  ✅ Data Upload & Management                                               │ │
│  │  ✅ Computation Result Export                                              │ │
│  │  ✅ Audit Logging & Compliance                                             │ │
│  │  ✅ WebSocket Real-time Updates                                            │ │
│  │  ✅ Error Handling & Validation                                            │ │
│  │                                                                             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              PENDING FEATURES                               │ │
│  │                                                                             │ │
│  │  🔄 Advanced Machine Learning Integration                                  │ │
│  │  🔄 Blockchain Integration for Audit Trails                                │ │
│  │  🔄 Mobile Application (iOS/Android)                                       │ │
│  │  🔄 Cloud Deployment (AWS/Azure)                                           │ │
│  │  🔄 Performance Optimization (Caching, CDN)                                │ │
│  │  🔄 Zero-Knowledge Proofs                                                  │ │
│  │  🔄 Hardware Security Modules (HSM)                                        │ │
│  │  🔄 Post-Quantum Cryptography                                              │ │
│  │                                                                             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```
