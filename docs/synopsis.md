# Project Synopsis: Kinetic Forge (Supply Chain Identity)

**PROJECT TITLE**: Resilient Supply Chain Identity Framework with AES-256 Field Encryption & Geo-Telemetry (Kinetic Forge)

**CANDIDATE DETAILS**:
- **Name**: [Your Name]
- **Register No**: 25879
- **Course**: [Your Course, e.g., BCA / B.Sc HS]
- **Institute**: Yenepoya Institute of Arts, Science, Commerce and Management
- **Place**: Balmatta, Mangalore
- **Date**: April 2026

**GUIDE DETAILS**:
- **Internal Guide**: [Internal Guide Name]
- **Designation**: Department of Computer Science
- **Institute**: YIASCM, Mangalore

---

### I. Title of the Project
**Kinetic Forge**: A Secure Supply Chain Identity Framework with Field-Level Encryption and Interactive Geo-Telemetry.

### II. Statement of the Problem
Logistics networks suffer from a lack of "Identity Visibility," where cargo data is often stored in plain text and accessible via weak credentials. This exposes the supply chain to data tampering and cargo theft. The problem is to implement a project that not only secures the identity of stakeholders (Suppliers, Managers) but also protects the operational data (Content, Origin) using industrial-grade encryption.

### III. Why this particular topic chosen?
Supply chain security is a global priority. This topic allows for the exploration of "Zero-Trust" data principles in a logistics context. It is technically challenging as it requires the integration of cryptographic libraries (Fernet) with real-time mapping technologies (Leaflet.js) to show how identity drives the movement of goods in a safe environment.

### IV. Objective and Scope
- **Objective**: To build an industrial command center where every logistical asset is encrypted and every user is multi-factor authenticated.
- **Scope**: Includes Supplier Dispatching, Logistics Management, and Managerial Oversight. The scope covers the full lifecycle of cargo from "In Transit" to "Delivered," secured by Google OAuth and TOTP.

### V. Methodology
A **Hybrid Waterfall-Agile Methodology** was used. The security requirements (Encryption/Auth) were defined upfront (Waterfall), while the interactive dashboards and mapping telemetry were developed in iterative sprints (Agile).

### VI. Process Description
- **Logistics Hub (Map)**: A real-time vector map that decodes geo-telemetry and renders active shipment flows.
- **Encryption Layer**: An ORM-integrated Fernet logic that protects cargo fields automatically.
- **Identity Hub**: Manages role-based redirects and MFA device synchronization.
- **Process Logic**: When a Supplier dispatches cargo, the data is encrypted via the `SecurityLayer` before hitting the database.

### VII. Resources and Limitations
- **Hardware**: High-speed internet for map tile rendering and OAuth flow.
- **Software**: Python, Flask, SQLAlchemy, cryptography.io (Fernet), Leaflet.js.
- **Limitations**: The system currently relies on static city-to-coordinate mapping. Future scope includes live GPS integration.

### VIII. Testing Technologies used
- **Security Testing**: Verifying the database ciphertext to ensure data at rest is unreadable.
- **User Interface Testing**: Cross-browser verification of the Leaflet map and the "Machined" dashboard aesthetic.
- **System Integration Test**: Matching Supplier dispatch IDs with Logistics update actions to ensure audit trail integrity.

### IX. Conclusion
Kinetic Forge demonstrates that logistical efficiency does not have to come at the cost of security. By intertwining Field-Level Encryption with Multi-Factor Authentication, the system provides a robust blueprint for modern, anti-hack logistical platforms.
