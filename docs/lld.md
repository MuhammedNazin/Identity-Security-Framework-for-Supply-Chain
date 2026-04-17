1. Introduction
1.1 Scope of the Document
This document provides the Low-Level Design (LLD) for the Kinetic Forge Supply Chain Identity system. It details:
•	Internal logic and code structure (Python/Flask).
•	Exact data schemas (SQLite database).
•	API endpoint specifications (request/response formats).
•	Security implementation (AES-256 for physical fields, Scrypt hashing, PyOTP, Google OAuth 2.0).
The LLD is intended for developers, security auditors, and the implementation team to build the system without ambiguity.
1.2 Intended Audience
•	Technical Lead / Industry Mentor
•	Implementation Engineers
•	Security Auditors
1.3 System Overview
Kinetic Forge is an encrypted logistics command center that guards transit data. The system:
•	Encrypts physical logistics fields (Origins, Destinations, Contents) using an ORM-based Property layer.
•	Authenticates stakeholders using corporate Google accounts combined with Scrypt-hashed fallbacks.
•	Enforces PyOTP-based TOTP for dispatch workflows.
•	Provides a secure geo-telemetry API for plotting vector animations on a live map via Leaflet.js.
________________________________________
2. System Design
2.1 Application Design
The application follows a Zero-Trust industrial pattern:
•	Presentation Layer: Machined Industrial UI (Jinja2 + Leaflet.js).
•	Application Layer: Flask (Python) with role-oriented logic (Manager, Logistics, Supplier).
•	Data Layer: SQLite Database with field-level AES encryption implemented at the Model level.
2.2 Process Flow
•	Request Layer: Hardened form views enforce CSRF tokens across all POST requests.
•	Logic Layer: Validates PyOTP secrets before allowing state transitions (e.g. from 'In Transit' to 'Delivered') or accessing detailed location feeds.
•	Transport Layer: Internal REST-like APIs providing decrypted database states downstream as GeoJSON equivalents to Leaflet.js vectors.
2.4 Components Design
2.4.1 Module: security_utils.py
Function	Input	Output	Description
encrypt_data(value: str) -> str	plaintext string	ciphertext	Symmetric AES encryption using Fernet derived from environment variables
decrypt_data(value: str) -> str	ciphertext	plaintext	Transparent decryption
2.4.2 Modules: models.py
•	Implements SQLite architecture using SQLAlchemy.
•	Defines @property logic for transparent decryption on read, and @setter logic for transparent encryption on write.
2.5 Key Design Considerations
1.	Field-level logic: Cargo payloads never sit in SQLite in plaintext, preventing physical server theft.
2.	Identity Orchestration: Google OAuth flows intercept new users and apply institutional mappings based on email, restricting new public signups to lowest-level 'Supplier' status.
2.6 API Catalogue
Endpoint	Method	Request Body	Response	Description
/supplier/dispatch	POST	item_name, origin, dest, qty	Redirect	Creates encrypted Cargo model.
/api/logistics/flows	GET	-	JSON Vector Array	Returns lat/lng of in-transit cargo.
/login/google/callback	GET	code	Session Cookie	Resolves Google openid payload, triggers 2FA prompt.
________________________________________
3. Data Design
3.1 Data Model
Table: User (SQLite)
Column Name	Data Type	Constraint	Description
id	INTEGER	PRIMARY KEY	Internal identifier
username	VARCHAR(150)	UNIQUE, NOT NULL	Display name
email	VARCHAR(150)	UNIQUE, NOT NULL	Institutional/Corporate email
password_hash	VARCHAR(256)	NULL	Scrypt hash (Nullable)
role	VARCHAR(50)	NOT NULL	Supplier, Logistics, Manager
google_id	VARCHAR(150)	UNIQUE, NULL	Google sub/openid
totp_secret	VARCHAR(32)	NULL	Base32 PyOTP seed
is_2fa_enabled	BOOLEAN	DEFAULT FALSE	Trigger for MFA pathway

Table: Cargo (SQLite)
Column Name	Data Type	Constraint	Description
id	INTEGER	PRIMARY KEY	Internal identifier
tracking_number	VARCHAR(100)	UNIQUE, NOT NULL	Auto-generated GUID
_content	VARCHAR(512)	NOT NULL	Encrypted item descriptor
_origin	VARCHAR(512)	-	Encrypted origin string
_destination	VARCHAR(512)	-	Encrypted destination string
origin_lat	FLOAT	-	Decimal origin coordinate
dest_lat	FLOAT	-	Decimal destination coordinate
status	VARCHAR(50)	DEFAULT 'In Transit'	Logistical state machine
supplier_id	INTEGER	FOREIGN KEY	Links to User table

3.2 Data Access Mechanism
•	Uses SQLAlchemy ORM object querying.
•	The `Cargo` object explicitly routes property calls (e.g., `cargo.origin`) through the encryption getter/setters transparently.
________________________________________
4. Interfaces
4.1 User Interface
The UI leverages standardized Flask templates with frontend security policies.
Pages:
•	Global Dashboard: Uses Leaflet.js and CartoCDN to plot tracking vectors.
•	Supplier Terminal: Restricted input forms for dispatching physical goods.
•	Authentication Portal: QR code generation for TOTP pairing, intercept views.
4.2 API Contracts (detailed)
GET /api/logistics/flows
•	Request data: None
•	Response framework (200): [{"id": 1, "coords": [[35.67, 139.65], [52.52, 13.40]]}]
________________________________________
5. State and Session Management
•	Relies on Flask's cryptographically signed session cookies to manage the MFA state machine (`pending_2fa_user_id`).
•	Logistical updates are stateless POST requests authenticated by the active session hash.
________________________________________
6. Caching
•	Rate limiting relies on memory stores (via `Flask-Limiter`) to track authentication failures and block abusive incoming API/login attempts (100/hour limit).
________________________________________
7. Non-Functional Requirements
7.1 Security Aspects
Aspect	Implementation
Encryption at rest	AES-256 (Fernet) logic on Cargo.
XSS Prevention	Flask-Talisman strictly limits CSP to self and verified CDNs (Leaflet, Carto).
CSRF Mitigation	Flask-WTF automatically appends hidden form validation tokens to state-changing logic routes.
7.2 Performance Aspects
•	Due to localized edge-computing of Leaflet.js vectors on the client side, backend map serialization easily operates under low-latency targeting.
