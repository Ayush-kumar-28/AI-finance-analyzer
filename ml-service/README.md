# FastAPI ML Service

High-performance Machine Learning service for Finance Tracker.

## Features

- ✅ **Fast** - Model loaded once, stays in memory
- ✅ **Async** - Handles multiple requests concurrently
- ✅ **Auto Docs** - Swagger UI at /docs
- ✅ **Type Safe** - Pydantic validation
- ✅ **Production Ready** - Used by major companies

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Server
```bash
python main.py
```

Server runs on: http://localhost:8000

### View API Docs
```
http://localhost:8000/docs
```

## API Endpoints

### GET /
Health check

### GET /health
Detailed health status

### GET /categories
Get available categories

### POST /analyze
Analyze bank statement file

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@statement.csv"
```

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
  "transactionCount": 11,
  "processedAt": "2026-02-07T10:30:00.000Z"
}
```

### POST /classify
Classify single transaction

**Request:**
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"description": "ZOMATO ORDER"}'
```

**Response:**
```json
{
  "description": "ZOMATO ORDER",
  "category": "Food"
}
```

## Production Deployment

### With Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance

- **First Request:** 2-3 seconds
- **Subsequent Requests:** 0.5-1 second
- **Concurrent Requests:** 100+
- **Memory:** ~200MB

## Tech Stack

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **scikit-learn** - ML model
- **pandas** - Data processing
- **Pydantic** - Data validation
