# Installation Guide: The Kinetic Forge (Supply Chain)

This guide provides instructions for setting up the "Identity Framework of Supply Chain" environment locally.

## Prerequisite Software
- Python 3.10 or higher
- Git (optional, for cloning)
- A modern web browser (Chrome/Edge/Firefox)
- A Google Cloud Account (for OAuth 2.0 configuration)
- An Authenticator App (Google Authenticator, Authy, or Microsoft Authenticator) installed on your mobile device.

## Step 1: Clone and Environment Setup

1. **Navigate to your workspace directory** and clone the repository (or extract the project files).
    ```bash
    cd "Identity framework of supply chain"
    ```

2. **Create a Virtual Environment** to isolate project dependencies.
    ```bash
    python -m venv .venv
    ```

3. **Activate the Virtual Environment**
    - On **Windows**:
      ```powershell
      .\.venv\Scripts\activate
      ```
    - On **macOS/Linux**:
      ```bash
      source .venv/bin/activate
      ```

## Step 2: Install Dependencies

With the virtual environment active, install the required packages. While a `requirements.txt` is standard, the core dependencies required for this framework are:

```bash
pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Flask-Talisman Flask-Limiter cryptography pyotp qrcode Authlib python-dotenv requests
```

*Note: If a `requirements.txt` is provided in the project root, you can simply run `pip install -r requirements.txt`.*

## Step 3: Configure the Secure Vault (`.env`)

The project uses `.env` files to keep sensitive keys out of the source code.

1. **Create a file named `.env`** in the root directory (`Identity framework of supply chain/.env`).
2. **Add the following structure** to the file:

    ```env
    # ==========================================
    # SUPPLY CHAIN (The Kinetic Forge) - Project 1
    # ==========================================
    SC_GOOGLE_CLIENT_ID=your-google-client-id-here
    SC_GOOGLE_CLIENT_SECRET=your-google-client-secret-here
    
    # Security Salts & Keys
    SC_SECRET_KEY=a-very-long-secure-random-string-123
    ```

3. **Acquire Google Credentials**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Navigate to **APIs & Services > Credentials**.
    - Create an **OAuth Client ID** (Type: Web application).
    - Add `http://127.0.0.1:5000/login/google/callback` to the **Authorized redirect URIs**.
    - Copy the generated Client ID and Client Secret into your `.env` file.

You are now ready to initialize the database and run the application. Proceed to the **Run Guide**.
