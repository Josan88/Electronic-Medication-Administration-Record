# Electronic Medication Administration Record (eMAR)

A Flask-based web application for managing and tracking medication administration records electronically.

## Features

- Patient Management
- Medication Tracking
- Administration Records
- Reports & Analytics

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd Electronic-Medication-Administration-Record
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

- Windows:
  ```bash
  .venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Set up environment variables:

- Copy `.env` and update the values as needed
- Change the `SECRET_KEY` in production

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
Electronic-Medication-Administration-Record/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .gitignore         # Git ignore file
├── README.md          # Project documentation
├── templates/         # HTML templates
│   └── index.html
└── static/           # Static files (CSS, JS, images)
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## API Endpoints

- `GET /` - Main application page
- `GET /api/health` - Health check endpoint

## Development

To run in development mode with auto-reload:

```bash
python app.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
