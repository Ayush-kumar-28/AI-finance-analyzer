# Finance Tracker Backend

Node.js + Express API server for Finance Tracker ML integration.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start server:
```bash
npm start
```

Or with auto-reload:
```bash
npm run dev
```

## API Endpoints

### POST /api/analyze
Upload and analyze bank statement file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (CSV, Excel, or PDF)

**Response:**
```json
{
  "income": 69170.0,
  "expense": 69791.0,
  "remaining_balance": -621.0,
  "categories": {
    "Education": 69000.0,
    "Food": 791.0
  },
  "fileName": "statement.csv",
  "processedAt": "2026-02-07T10:30:00.000Z"
}
```

### GET /api/categories
Get list of available categories.

### GET /api/health
Health check endpoint.

## Environment Variables

- `PORT` - Server port (default: 5000)
- `NODE_ENV` - Environment (development/production)
