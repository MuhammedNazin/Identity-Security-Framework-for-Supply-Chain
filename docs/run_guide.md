# Run Guide: The Kinetic Forge (Supply Chain)

This guide details how to launch, seed, and operate the Supply Chain Identity Framework.

## 1. Initializing the Database

Before starting the server for the first time (or if you need to wipe and reset the data), you must run the final seeder script. This script builds the SQL tables and populates them with high-precision geo-telemetry mock data.

1. Ensure your virtual environment is active.
2. Navigate to the supply chain directory:
   ```bash
   cd "Identity framework of supply chain/supply_chain_auth"
   ```
3. Run the database seeder:
   ```bash
   python seed_sc_final.py
   ```
   *Expected Output*: "Done. Database has been restructured and seeded with physical locations."

### Default Seeded Accounts
The seeder creates basic accounts with distinct roles. All passwords are set to the hashed equivalent of their listed values.
- **Global Operations**: `25879@yenepoya.edu.in` / `Nachu@123`
- **Supplier Team**: `Mohammadnazin7@gmail.com` / `test`
- **Logistics**: `Muhammednazin41@gmail.com` / `test`

## 2. Launching the Hub

To start the Flask WSGI development server:

```bash
python app.py
```
The application will be accessible at: **http://127.0.0.1:5000**

## 3. Operating the Hub (Role-Based Workflows)

### 3.1 Establishing Multi-Factor Authentication (MFA)
Regardless of your role, MFA is enforced.
1. Log in with your standard credentials, or simply click **"ID via Google"**.
2. If this is your first time, navigate to the `⚠️ Set Up MFA` link in the top navigation bar.
3. Scan the QR code with your mobile Authenticator App.
4. Enter the 6-digit code to bind the device to your account.
5. On subsequent logins, you will be intercepted and required to enter a code from your device.

### 3.2 Supplier Workflow (Dispatching Cargo)
1. Log in using a Supplier account (or via a new Google OAuth account, which defaults to Supplier).
2. You will arrive at the **Supplier HUD**.
3. View your specific Inventory Manifest (cargo assigned exclusively to you).
4. Click **"+ Dispatch Cargo"** to open the dispatch modal.
5. Enter the Item Name, Quantity, and select the Origin/Destination hubs. Click Authorize.
6. The new cargo is encrypted and injected into the network.

### 3.3 Logistics Workflow (Status Management)
1. Log in with the Logistics account (`logs@sc.com`).
2. You will arrive at the **Logistics HUD**.
3. You will see a ledger of all active cargo currently "In Transit".
4. To simulate movement, use the action buttons to advance a cargo's status from "In Transit" to "Delivered" or "Held".

### 3.4 Manager Workflow (Global Telemetry)
1. Log in with the Manager account (`manager@sc.com`).
2. You will arrive at the **Global Operations Command Center**.
3. View the **Interactive Leaflet Map**. The map actively queries the `/api/logistics/flows` endpoint. You will see animated vector lines reflecting physical cargo moving between hubs.
4. Note that if Logistics marks a shipment as "Delivered", it drops off the live animated map, and the overall system "Efficiency" dial adjusts dynamically.
