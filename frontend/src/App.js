import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import InvestmentAdvice from './components/InvestmentAdvice';
import axios from 'axios';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showInvestmentAdvice, setShowInvestmentAdvice] = useState(false);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setData(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setData(response.data);
    } catch (err) {
      // FastAPI returns errors in 'detail' field
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.error || 
                          err.message || 
                          'Failed to process file. Please check your file format.';
      setError(errorMessage);
      console.error('Upload error:', err);
      console.error('Error details:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setData(null);
    setError(null);
    setShowInvestmentAdvice(false);
  };

  const handleShowInvestmentAdvice = () => {
    setShowInvestmentAdvice(true);
  };

  const handleBackToDashboard = () => {
    setShowInvestmentAdvice(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>💰 Finance Tracker</h1>
        <p>AI-Powered Transaction Analysis</p>
      </header>

      <main className="App-main">
        {!data && !loading && (
          <FileUpload 
            onFileUpload={handleFileUpload} 
            error={error} 
          />
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing your transactions...</p>
          </div>
        )}

        {data && !loading && !showInvestmentAdvice && (
          <Dashboard 
            data={data} 
            onReset={handleReset}
            onShowInvestmentAdvice={handleShowInvestmentAdvice}
          />
        )}

        {data && !loading && showInvestmentAdvice && (
          <InvestmentAdvice 
            financialData={data}
            onBack={handleBackToDashboard}
          />
        )}
      </main>

      <footer className="App-footer">
        <p>Powered by Ayush Kumar</p>
      </footer>
    </div>
  );
}

export default App;
