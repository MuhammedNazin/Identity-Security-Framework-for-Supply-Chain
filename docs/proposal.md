# Project Proposal: Enhanced Identity Security Framework for Supply Chain (PRJN26-144)

## 1. Problem Statement
Global supply chains are increasingly targeted by sophisticated cyber-attacks. Traditional single-factor authentication (email/password) is no longer sufficient to protect sensitive logistics data. The primary security challenge is to provide a user-friendly yet highly secure method for stakeholders to access the system while preventing unauthorized breaches and credential theft.

## 2. Project Objectives
This project aims to implement a next-generation Identity Security Framework for the supply chain sector, integrating modern social login and multi-factor authentication.
- **Secure Authentication**: Traditional hashed password login via Flask-Login.
- **Social Integration**: Implement **Google Sign-On (OAuth 2.0)** to provide a streamlined and secure institutional entry point.
- **Multi-Factor Authentication (MFA)**: Integrate **Time-based One-Time Passwords (TOTP)** to protect against stolen credentials.
- **Granular Authorization**: Enforce role-based access control (RBAC) for Suppliers, Managers, and Logistics Coordinators.

## 3. Scope of Work
- **Advanced Auth Engine**: Flask server utilizing `Authlib` for Google OAuth and `PyOTP` for 2FA.
- **Enhanced Identity Features**:
  - Unified login flow supporting password and Google Sign-On.
  - Optional but encouraged 2FA setup with QR code generation.
  - Secure state management for "pending 2FA" authentication states.
- **Role-Specific Dashboards**: Custom interfaces for each supply chain stakeholder.
- **Institution Header**: [Your Institution Name] | [Student Name] | [Guide Name].

## 4. Timeline (45 Days)
| Week | Focus Area | Deliverables |
|------|------------|--------------|
| 1-2 | Architecture & Core | Proposal, HLD, Basic Login |
| 3-4 | Security Upgrades | Google OAuth, TOTP logic, 2FA setup |
| 5-6 | RBAC & UI | Role dashboards, Premium Glassmorphism UI |
| 7-8 | Finalization | LLD, Final Report, Security Testing |

## 5. Risk Assessment & Mitigation
| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| **Credential Theft** | High | Mitigation: **TOTP-based 2FA** ensures that even if a password is stolen, the account remains secure. |
| **Phishing** | Medium | Mitigation: Use of **Google Sign-On** leverages Google's advanced security and reduces common password-based attacks. |
| **Session Hijacking** | Medium | Implementation of secure session cookies and state validation during 2FA. |

## 6. Conclusion
By integrating Google Sign-On and 2FA, this framework provides an enterprise-ready security posture for supply chain management, ensuring that only verified and multi-factor authenticated users can interact with critical logistics data.
