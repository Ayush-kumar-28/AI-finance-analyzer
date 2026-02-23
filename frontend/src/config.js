/**
 * Application Configuration
 * Centralized configuration for API endpoints and settings
 */

const config = {
  // API Base URL - uses proxy in development, can be overridden for production
  apiBaseUrl: process.env.REACT_APP_API_URL || '',
  
  // API Endpoints
  endpoints: {
    analyze: '/api/analyze',
    categories: '/api/categories',
    health: '/api/health',
    learningStats: '/api/learning/stats',
    learningRetrain: '/api/learning/retrain',
  },
  
  // File upload settings
  upload: {
    maxSize: 10 * 1024 * 1024, // 10MB
    acceptedFormats: ['.csv', '.xlsx', '.xls', '.pdf'],
  },
  
  // Learning settings
  learning: {
    statsRefreshInterval: 5000, // 5 seconds
    minSamplesForRetrain: 50,
  },
};

export default config;
