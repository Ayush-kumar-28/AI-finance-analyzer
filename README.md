# 💰 Finance Tracker - AI-Powered Transaction Classifier

An intelligent finance tracking application that automatically categorizes bank transactions using Machine Learning, provides investment advice, and learns from user corrections.

## 🌟 Features

- **Automatic Transaction Classification** - ML-powered categorization of expenses and income
- **Multi-Format Support** - Upload CSV, Excel, or PDF bank statements
- **Smart Data Cleaning** - Adaptive cleaning pipeline that learns from different bank formats
- **Investment Advisor** - AI-generated personalized investment recommendations
- **Online Learning** - Model improves over time with user feedback
- **Real-time Analytics** - Visual dashboards with spending insights
- **PostgreSQL Storage** - Persistent data storage with full transaction history

## 🏗️ Architecture

```
Frontend (React)  →  Backend (Node.js)  →  ML Service (FastAPI)  →  PostgreSQL
    Vercel              Render                  Render                Render
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/finance-tracker.git
cd finance-tracker
```

2. **Set up ML Service**
```bash
cd ml-service
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database URL
uvicorn main:app --reload --port 8000
```

3. **Set up Backend**
```bash
cd backend
npm install
cp .env.example .env
# Edit .env with ML_SERVICE_URL=http://localhost:8000
npm start
```

4. **Set up Frontend**
```bash
cd frontend
npm install
npm start
```

5. **Access the app**
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- ML Service: http://localhost:8000

## 📦 Deployment

### Quick Deploy (20 minutes)

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for step-by-step instructions.

### Detailed Guide

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive deployment documentation.

### Deployment Platforms

- **Frontend**: Vercel (Free tier)
- **Backend**: Render (Free tier)
- **ML Service**: Render (Free tier)
- **Database**: Render PostgreSQL (Free tier)

## 🛠️ Tech Stack

### Frontend
- React 18
- Recharts (data visualization)
- Axios (API calls)
- React Dropzone (file uploads)

### Backend
- Node.js + Express
- Multer (file handling)
- Axios (ML service communication)

### ML Service
- FastAPI (Python web framework)
- Scikit-learn (ML models)
- Pandas (data processing)
- SQLAlchemy (database ORM)
- PDFPlumber (PDF parsing)

### Database
- PostgreSQL (production)
- SQLite (development)

## 📊 ML Pipeline

```
Upload → Data Cleaning → PostgreSQL → NLP Processing → Classification → Summary
```

1. **Data Cleaning**: Adaptive pipeline learns bank statement formats
2. **Storage**: Transactions stored in PostgreSQL
3. **NLP**: Text preprocessing and feature extraction
4. **Classification**: SVM model categorizes transactions
5. **Learning**: Model improves with user feedback

## 🎯 API Endpoints

### Backend (Node.js)
- `POST /api/analyze` - Upload and analyze bank statement
- `GET /api/categories` - Get available categories
- `GET /api/health` - Health check
- `POST /api/investment/advice` - Get investment recommendations

### ML Service (FastAPI)
- `POST /analyze` - Process transactions
- `POST /classify` - Classify single transaction
- `GET /learning/stats` - Get learning statistics
- `POST /learning/retrain` - Trigger model retraining
- `GET /health` - Health check

## 📁 Project Structure

```
finance-tracker/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.js
│   │   └── config.js     # API configuration
│   └── package.json
├── backend/              # Node.js backend
│   ├── server.js         # Express server
│   ├── uploads/          # Temporary file storage
│   └── package.json
├── ml-service/           # FastAPI ML service
│   ├── main.py           # FastAPI app
│   ├── database.py       # Database models
│   ├── db_manager.py     # Database operations
│   ├── data_cleaning_pipeline.py
│   ├── online_learning.py
│   ├── investment_advisor.py
│   └── requirements.txt
├── app/                  # ML models and services
│   ├── models/           # Trained models (.pkl)
│   ├── services/         # Classification logic
│   └── utils/            # Text processing
└── training/             # Model training scripts

```

## 🔧 Configuration

### Environment Variables

**ML Service** (`.env`)
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

**Backend** (`.env`)
```env
PORT=5000
ML_SERVICE_URL=http://localhost:8000
```

**Frontend** (`.env.local`)
```env
REACT_APP_API_URL=http://localhost:5000
```

## 🧪 Testing

### Test ML Service
```bash
curl http://localhost:8000/health
```

### Test Backend
```bash
curl http://localhost:5000/api/health
```

### Upload Test File
Use the sample file: `bank_transactions_120.xlsx`

## 📈 Monitoring

- **Render Dashboard**: View logs and metrics
- **Vercel Dashboard**: Monitor deployments and bandwidth
- **Database**: Check PostgreSQL usage in Render

## 🐛 Troubleshooting

### Cold Starts
Free tier services sleep after 15 minutes. First request takes 30-60 seconds.

**Solution**: Use UptimeRobot to ping services every 14 minutes.

### CORS Errors
Check that `REACT_APP_API_URL` is set correctly in Vercel.

### Database Connection
Use **Internal Database URL** from Render, not External.

### Model Not Loading
Ensure `.pkl` files are in `ml-service/app/models/` directory.

## 🔐 Security

- Environment variables for all secrets
- HTTPS enabled on all platforms
- CORS configured for specific origins
- File upload validation and size limits
- SQL injection prevention with SQLAlchemy ORM

## 📝 License

MIT License - feel free to use this project for learning or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📞 Support

- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment issues
- Review [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for quick setup
- Open an issue on GitHub for bugs

## 🎉 Acknowledgments

- Scikit-learn for ML capabilities
- FastAPI for high-performance API
- React for beautiful UI
- Render and Vercel for free hosting

---

**Built with ❤️ for better financial management**

🌟 Star this repo if you find it helpful!
