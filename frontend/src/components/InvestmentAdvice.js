import React, { useState, useEffect } from 'react';
import './InvestmentAdvice.css';

function InvestmentAdvice({ financialData, onBack }) {
  const [advice, setAdvice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInvestmentAdvice();
  }, []);

  const fetchInvestmentAdvice = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/investment/advice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          balance: financialData.remaining_balance,
          income: financialData.income,
          expense: financialData.expense
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAdvice(data);
      } else {
        setError('Failed to fetch investment advice');
      }
    } catch (err) {
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  if (loading) {
    return (
      <div className="investment-advice">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Analyzing your finances and market conditions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="investment-advice">
        <div className="error-container">
          <p>{error}</p>
          <button onClick={onBack}>Go Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="investment-advice">
      <div className="advice-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Dashboard
        </button>
        <h1>💰 Investment Advice</h1>
        <p className="subtitle">Personalized recommendations based on your financial situation</p>
      </div>

      {/* Financial Summary */}
      <div className="financial-summary-card">
        <h2>Your Financial Overview</h2>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="label">Available Balance</span>
            <span className="value">{formatCurrency(advice.balance)}</span>
          </div>
          <div className="summary-item">
            <span className="label">Monthly Income</span>
            <span className="value">{formatCurrency(advice.income)}</span>
          </div>
          <div className="summary-item">
            <span className="label">Monthly Expense</span>
            <span className="value">{formatCurrency(advice.expense)}</span>
          </div>
          <div className="summary-item highlight">
            <span className="label">Savings Rate</span>
            <span className="value">{advice.savings_rate}%</span>
          </div>
        </div>
      </div>

      {/* Risk Profile */}
      <div className="risk-profile-card">
        <h2>Your Risk Profile</h2>
        <div className="risk-badge">{advice.risk_profile} Risk</div>
        <p className="risk-description">{advice.advice_summary}</p>
      </div>

      {/* Investment Capacity */}
      <div className="capacity-card">
        <h2>Investment Capacity</h2>
        <div className="capacity-breakdown">
          <div className="capacity-item">
            <span className="capacity-label">Emergency Fund (20%)</span>
            <span className="capacity-value">
              {formatCurrency(advice.investment_capacity.emergency_fund)}
            </span>
          </div>
          <div className="capacity-item highlight">
            <span className="capacity-label">Available to Invest (80%)</span>
            <span className="capacity-value">
              {formatCurrency(advice.investment_capacity.investable_amount)}
            </span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="recommendations-section">
        <h2>📊 Recommended Investment Portfolio</h2>
        {advice.recommendations.map((rec, index) => (
          <div key={index} className="recommendation-card">
            <div className="rec-header">
              <div className="rec-title">
                <span className="rec-rank">#{rec.rank}</span>
                <h3>{rec.investment}</h3>
                <span className={`action-badge ${rec.action.toLowerCase().replace(/ /g, '-').replace('---', '-')}`}>
                  {rec.action}
                </span>
                {rec.market_signal && (
                  <span className={`signal-badge ${rec.market_signal.toLowerCase().replace(/ /g, '-')}`}>
                    {rec.market_signal}
                  </span>
                )}
              </div>
              <div className="rec-allocation">
                <span className="allocation-amount">{formatCurrency(rec.allocation)}</span>
                <span className="allocation-percent">{rec.percentage}</span>
              </div>
            </div>

            <p className="rec-reason">{rec.reason}</p>

            <div className="market-info">
              <div className="market-item">
                <span className="market-label">Current Price</span>
                <span className="market-value">{rec.market_data.current_price}</span>
              </div>
              <div className="market-item">
                <span className="market-label">24h Change</span>
                <span className={`market-value ${rec.market_data.trend}`}>
                  {rec.market_data.change_24h}
                </span>
              </div>
              <div className="market-item">
                <span className="market-label">Expected Return</span>
                <span className="market-value">{rec.market_data.expected_return}</span>
              </div>
              <div className="market-item">
                <span className="market-label">Risk Level</span>
                <span className="market-value">{rec.market_data.risk_level}</span>
              </div>
              {rec.market_data.data_source && (
                <div className="market-item full-width">
                  <span className="market-label">Data Source</span>
                  <span className="market-value data-source">{rec.market_data.data_source}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Projections */}
      <div className="projections-section">
        <h2>📈 Potential Returns</h2>
        <p className="projections-note">{advice.projections.note}</p>
        
        <div className="projections-grid">
          {Object.entries(advice.projections.projections).map(([period, scenarios]) => (
            <div key={period} className="projection-card">
              <h3>{period.replace('_', ' ').toUpperCase()}</h3>
              <div className="scenarios">
                <div className="scenario conservative">
                  <span className="scenario-label">Conservative (8%)</span>
                  <span className="scenario-value">{formatCurrency(scenarios.conservative)}</span>
                </div>
                <div className="scenario moderate">
                  <span className="scenario-label">Moderate (12%)</span>
                  <span className="scenario-value">{formatCurrency(scenarios.moderate)}</span>
                </div>
                <div className="scenario aggressive">
                  <span className="scenario-label">Aggressive (18%)</span>
                  <span className="scenario-value">{formatCurrency(scenarios.aggressive)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="disclaimer">
        <p>
          ⚠️ <strong>Disclaimer:</strong> This advice is for informational purposes only and should not be considered as financial advice. 
          Market conditions change rapidly. Please consult with a certified financial advisor before making investment decisions.
        </p>
      </div>
    </div>
  );
}

export default InvestmentAdvice;
