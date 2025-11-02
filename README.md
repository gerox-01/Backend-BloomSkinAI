# BloomSkin API

Backend API for BloomSkin AI-Powered Skincare Platform using Firebase.

## Quick Start

### 1. First Time Setup

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies

### 2. Run the Server

```bash
./run.sh
```

The server will start on `http://localhost:8000`

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once the server is running, visit:

- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

## Project Structure

```
Backend-BloomSkin/
├── app/                      # Application code
│   ├── api/                  # API endpoints
│   ├── core/                 # Core configuration
│   ├── domain/               # Business logic
│   └── infrastructure/       # External services (Firebase)
├── firebase-credentials.json # Firebase service account
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
└── run.sh                    # Run script
```

## Configuration

Firebase credentials are configured in:
- `.env` - Environment variables
- `firebase-credentials.json` - Service account credentials

Project ID: `bloomskinai-412aa`
