const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');

const app = express();
const PORT = process.env.PORT || 5000;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  }
});

const upload = multer({
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.csv', '.xlsx', '.xls', '.pdf'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only CSV, Excel, and PDF files are allowed.'));
    }
  }
});

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const mlHealth = await axios.get(`${ML_SERVICE_URL}/health`);
    res.json({
      status: 'ok',
      backend: 'running',
      mlService: mlHealth.data
    });
  } catch (error) {
    res.status(503).json({
      status: 'degraded',
      backend: 'running',
      mlService: 'unavailable',
      error: error.message
    });
  }
});

// Get categories list
app.get('/api/categories', async (req, res) => {
  try {
    const response = await axios.get(`${ML_SERVICE_URL}/categories`);
    res.json(response.data);
  } catch (error) {
    console.error('ML Service error:', error.message);
    // Fallback to hardcoded categories
    res.json({
      income: ['Income', 'Cashback'],
      expense: [
        'Food',
        'Transport',
        'ATM',
        'Shopping',
        'Utilities',
        'Rent',
        'Entertainment',
        'Transfer',
        'Education',
        'Others'
      ]
    });
  }
});

// File upload and analysis endpoint
app.post('/api/analyze', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePath = req.file.path;
    console.log('Processing file:', req.file.originalname);

    // Create form data to send to ML service
    const formData = new FormData();
    formData.append('file', fs.createReadStream(filePath), {
      filename: req.file.originalname,
      contentType: req.file.mimetype
    });

    try {
      // Call FastAPI ML service
      const response = await axios.post(`${ML_SERVICE_URL}/analyze`, formData, {
        headers: {
          ...formData.getHeaders()
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity
      });

      // Clean up uploaded file
      fs.unlinkSync(filePath);

      // Return ML service response
      res.json(response.data);

    } catch (mlError) {
      // Clean up uploaded file
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }

      console.error('ML Service error:', mlError.response?.data || mlError.message);
      
      res.status(mlError.response?.status || 500).json({
        error: 'ML service error',
        details: mlError.response?.data?.detail || mlError.message
      });
    }

  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ 
      error: 'Server error', 
      details: error.message 
    });
  }
});

// Learning endpoints
app.get('/api/learning/stats', async (req, res) => {
  try {
    const response = await axios.get(`${ML_SERVICE_URL}/learning/stats`);
    res.json(response.data);
  } catch (error) {
    console.error('ML Service error:', error.message);
    res.status(500).json({ 
      error: 'Failed to fetch learning stats', 
      details: error.message 
    });
  }
});

app.post('/api/learning/retrain', async (req, res) => {
  try {
    const response = await axios.post(`${ML_SERVICE_URL}/learning/retrain`);
    res.json(response.data);
  } catch (error) {
    console.error('ML Service error:', error.message);
    res.status(500).json({ 
      error: 'Failed to retrain model', 
      details: error.message 
    });
  }
});

// Investment advice endpoint
app.post('/api/investment/advice', async (req, res) => {
  try {
    const { balance, income, expense } = req.body;
    
    if (!balance || !income || !expense) {
      return res.status(400).json({
        error: 'Missing required fields',
        details: 'balance, income, and expense are required'
      });
    }
    
    const response = await axios.post(`${ML_SERVICE_URL}/investment/advice`, {
      balance,
      income,
      expense
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('ML Service error:', error.message);
    res.status(500).json({ 
      error: 'Failed to get investment advice', 
      details: error.message 
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!', 
    details: err.message 
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 API endpoints:`);
  console.log(`   - POST /api/analyze (upload file)`);
  console.log(`   - GET  /api/categories`);
  console.log(`   - GET  /api/health`);
  console.log(`   - GET  /api/learning/stats`);
  console.log(`   - POST /api/learning/retrain`);
  console.log(`   - POST /api/investment/advice`);
});
