import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import InvestmentAdvice from './components/InvestmentAdvice';
import axios from 'axios';
import config from './config';

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
      const apiUrl = `${config.apiBaseUrl}${config.endpoints.analyze}`;
      const response = await axios.post(apiUrl, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setData(response.data);
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        err.response?.data?.error ||
        err.message ||
        'Failed to process file. Please check your file format.';
      setError(errorMessage);
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setData(null);
    setError(null);
    setShowInvestmentAdvice(false);
  };

  const handleShowInvestmentAdvice = () => setShowInvestmentAdvice(true);
  const handleBackToDashboard    = () => setShowInvestmentAdvice(false);

  return (
    <div className="App">
      <div className="App-bg-grid" aria-hidden="true" />
      <header className="App-header">
        <div className="header-brand">
          <div className="header-logo-icon">💰</div>
          <div className="header-brand-text">
            <span className="header-brand-name">Finance Tracker</span>
            <span className="header-brand-tag">AI Powered</span>
          </div>
        </div>
        <div className="header-badge">
          <span className="header-badge-dot" />
          ML Active
        </div>
      </header>

      <main className="App-main">
        {!data && !loading && (
          <FileUpload onFileUpload={handleFileUpload} error={error} />
        )}

        {loading && (
          <div className="loading-container">
            <div className="loading-spinner-wrap">
              <div className="spinner" />
              <div className="spinner-inner" />
            </div>
            <p className="loading-text">Analyzing your transactions…</p>
            <p className="loading-subtext">AI is classifying your financial data</p>
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
        <p>Built by <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>Ayush Kumar</span></p>
        <span>·</span>
        <p>Powered by Machine Learning</p>
      </footer>
    </div>
  );
}

export default App;
