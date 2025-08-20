# Screenplay Generator Backend

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The server will start on http://localhost:8000

## API Endpoint

POST /generate-story
- Body: {"user_input": "Your story prompt here"}
- Returns: JSON with genre, tone, outline, scene, and dialogue