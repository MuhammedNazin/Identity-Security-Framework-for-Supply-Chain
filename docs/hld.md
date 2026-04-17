1. Introduction
1.1 Scope of the Document
This document provides the High-Level Design (HLD) for the Kinetic Forge Supply Chain Identity system. It details:
•	Broad architectural structure highlighting isolated logistical nodes.
•	Comprehensive data schemas (SQLite) covering AES-256 field-level encryption for origins, destinations, and physical item descriptors.
•	Comprehensive API endpoint specifications controlling geo-spatial logistics data.
•	Security implementation strategy including Scrypt hashing, PyOTP-based TOTP intercepts, and Institutional Google OAuth 2.0 mapping.
•	Operational tracking strategies via Live Vector Telemetry.
The HLD serves as the primary architectural blueprint, capturing 70-80% of the project's entire structural and functional integrity.

1.2 Intended Audience
•	Technical Lead / Industry Mentor
•	Implementation Engineers
•	Security Auditors

1.3 System Overview
Kinetic Forge is an encrypted logistics command center that guards sensitive transit data. The system:
•	Enforces PyOTP-based TOTP workflows before pushing operational payload states or accessing command APIs.
•	Authenticates stakeholders utilizing corporate Google accounts combined with Scrypt-hashed fallbacks mapping automatically to Supplier, Logistics, or Manager roles.
•	Encrypts physical logistics fields via property-based SQLite ORM configurations transparently.
•	Provides a secure, high-density geo-telemetry JSON API for plotting active logistics vectors via interactive Leaflet.js rendering on the dashboard.
________________________________________
2. System Design
2.1 Application Design
The application adheres to a Zero-Trust industrial tracking pattern:
•	Presentation Layer: Machined Industrial UI (Jinja2 + Leaflet.js overlay with dark mode semantics).
•	Application Layer: Flask (Python) with hardline role-oriented logic segregating command input functions per role type.
•	Data Layer: SQLite Database containing `_encrypted` attributes protecting physical fields directly on the disk.

2.2 Process Flow
•	Authentication: Initial entry validates either Google tokens or Scrypt hashes. If MFA is flagged active, it halts the context in memory over `verify_2fa`.
•	Operational Flow (Dispatch): A Supplier enters physical origin/dest values. The backend automatically associates them with geo-located floating coordinates, pushes the strings through the AES cipher, and writes to SQLite as `Cargo`.
•	Tracking Flow: The `Manager` interface routinely polls the telemetry endpoint to map coordinates onto global SVG layers.

2.3 Information Flow
•	Request Layer: Hardened form views enforce CSRF tokens across all POST dispatch and update requests. 
•	Transport Layer (Telemetry): Internal REST-like APIs providing decrypted database states downstream directly as formatted GeoJSON equivalents to build active SVG vectors.

2.4 Components Design
2.4.1 Module: security_utils.py
Function	Input	Output	Description
encrypt_data(value: str) -> str	plaintext string	ciphertext	Symmetric AES encryption using Fernet derived from environment variables
decrypt_data(value: str) -> str	ciphertext	plaintext	Transparent decryption layer triggered by `@property` ORM getters.

2.5 Key Design Considerations
1.	Field-level logic: Cargo payloads never sit in SQLite in plaintext, specifically guarding against raw physical server theft.
2.	Identity Orchestration: Google OAuth flows intercept new users and apply institutional mappings based on email filtering (`Mohammadnazin7@gmail.com` -> Supplier, `Muhammednazin41@gmail.com` -> Logistics).

2.6 API Catalogue
Endpoint	Method	Request Body	Response	Description
/supplier/dispatch	POST	item_name, origin, dest, qty	302 Redirect	Triggers encryption framework and generates new Cargo model.
/api/logistics/flows	GET	-	JSON Vector Array	Secure REST access returning live lat/lng of in-transit cargo.
/login/google/callback	GET	code	Session Cookie	Resolves internal Google openid payload, triggers subsequent 2FA intercepts securely.
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
id	INTEGER	PRIMARY KEY	Internal tracking UUID equivalent
tracking_number	VARCHAR(100)	UNIQUE, NOT NULL	Auto-generated external ID
_content	VARCHAR(512)	NOT NULL	Encrypted item descriptor
_origin	VARCHAR(512)	-	Encrypted origin string
_destination	VARCHAR(512)	-	Encrypted destination string
origin_lat	FLOAT	-	Decimal origin coordinate
dest_lat	FLOAT	-	Decimal destination coordinate
status	VARCHAR(50)	DEFAULT 'In Transit'	Logistical state machine indicator
supplier_id	INTEGER	FOREIGN KEY	Links physical good to User table

3.2 Data Access Mechanism
•	Uses SQLAlchemy ORM object querying. The `Cargo` object explicitly routes property calls (e.g., `cargo.origin`) through the encryption getter/setters transparently to ensure code maintainability inside template contexts.

3.3 Data Retention Policies
•	The tracking metrics rely heavily on timestamps `created_at` and `updated_at`. Shipments are placed into 'Delivered' status but are kept persistently to fulfill historical network-telemetry aggregates.

3.4 Data Migration
•	Dynamic DB wipe processes initialize standard hardcoded locations using `seed_sc_final.py`. 
________________________________________
4. Interfaces
4.1 User Interface
The UI leverages standardized Flask templates unified under a dark, machined industrial theme.
•	Global Dashboard: Uses Leaflet.js intersecting with active DOM nodes plotting tracking vectors overlaid on maps.
•	Supplier Terminal: Restricted input forms for dispatching physical goods into the secure ledger.
•	Logistics Terminal: State adjustment tools for controlling transit statuses.

4.2 API Contracts (detailed)
GET /api/logistics/flows
•	Request data: None
•	Response framework (200 OK): [{"id": 1, "coords": [[35.67, 139.65], [52.52, 13.40]], "quantity": 120}]
________________________________________
5. State and Session Management
•	Relies primarily on Flask's cryptographically signed session cookies to manage the critical MFA state machine (`pending_2fa_user_id`). Logistical updates are stateless POST requests fully verified via session bindings.

6. Caching
•	Rate limiting relies on purely memory-driven tracking configurations implemented centrally within `Flask-Limiter` preventing external brute-force credential stuffing.

7. Non-Functional Requirements
7.1 Security Aspects
Encryption at rest: AES-256 logic embedded implicitly over sensitive shipment identities.
XSS Prevention: Flask-Talisman limits CSP constraints specifically to CDN execution policies (Leaflet js scripts safe paths).
CSRF Mitigation: Flask-WTF injects form validation tokens behind standard post actions universally.

7.2 Performance Aspects
By heavily pushing processing logic onto the client rendering engine (Leaflet mapping), the backend REST endpoints execute hyper-optimized raw JSON serialization generating millisecond retrieval latencies.
