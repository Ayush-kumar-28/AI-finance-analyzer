import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import './Dashboard.css';
import config from '../config';

const COLORS = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe',
  '#43e97b', '#fa709a', '#fee140', '#30cfd0',
  '#a8edea', '#fed6e3'
];

function Dashboard({ data, onReset, onShowInvestmentAdvice }) {
  const { income, expense, remaining_balance, categories, fileName } = data;
  const [learningStats, setLearningStats] = React.useState(null);
  const [retraining, setRetraining] = React.useState(false);

  // Fetch learning stats
  React.useEffect(() => {
    fetchLearningStats();
    const interval = setInterval(fetchLearningStats, config.learning.statsRefreshInterval);
    return () => clearInterval(interval);
  }, []);

  const fetchLearningStats = async () => {
    try {
      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.learningStats}`);
      const stats = await response.json();
      setLearningStats(stats);
    } catch (error) {
      console.error('Failed to fetch learning stats:', error);
    }
  };

  const handleRetrain = async () => {
    setRetraining(true);
    try {
      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.learningRetrain}`, {
        method: 'POST'
      });
      const result = await response.json();
      alert(result.message || 'Model retrained successfully!');
      fetchLearningStats();
    } catch (error) {
      alert('Failed to retrain model: ' + error.message);
    } finally {
      setRetraining(false);
    }
  };

  // Prepare data for charts
  const categoryData = Object.entries(categories).map(([name, value]) => ({
    name,
    value: parseFloat(value)
  }));

  const summaryData = [
    { name: 'Income', value: parseFloat(income), color: '#43e97b' },
    { name: 'Expense', value: parseFloat(expense), color: '#fa709a' }
  ];

  const formatCurrency = (value) => {
    return `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  const balanceColor = remaining_balance >= 0 ? '#43e97b' : '#fa709a';

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h2>Financial Analysis</h2>
          <p className="file-name">📄 {fileName}</p>
        </div>
        <div className="header-buttons">
          <button className="invest-advice-button" onClick={onShowInvestmentAdvice}>
            💡 Invest Advice
          </button>
          <button className="reset-button" onClick={onReset}>
            Upload New File
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card income">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <p className="card-label">Total Income</p>
            <p className="card-value">{formatCurrency(income)}</p>
          </div>
        </div>

        <div className="summary-card expense">
          <div className="card-icon">💸</div>
          <div className="card-content">
            <p className="card-label">Total Expense</p>
            <p className="card-value">{formatCurrency(expense)}</p>
          </div>
        </div>

        <div className={`summary-card balance ${remaining_balance >= 0 ? 'positive' : 'negative'}`}>
          <div className="card-icon">{remaining_balance > 0 ? '✅' : '⚖️'}</div>
          <div className="card-content">
            <p className="card-label">Balance</p>
            <p className="card-value" style={{ color: remaining_balance > 0 ? balanceColor : '#666' }}>
              {formatCurrency(remaining_balance)}
            </p>
          </div>
        </div>
      </div>

      {/* Learning Progress Section */}
      {learningStats && (
        <div className="learning-progress-card">
          <div className="learning-header">
            <div>
              <h3>🤖 AI Learning Progress</h3>
              <p className="learning-subtitle">
                System learns from every upload to improve accuracy
              </p>
            </div>
            <button
              className={`retrain-button ${!learningStats.ready_for_retrain ? 'disabled' : ''}`}
              onClick={handleRetrain}
              disabled={!learningStats.ready_for_retrain || retraining}
            >
              {retraining ? '⏳ Retraining...' : '🔄 Retrain Model'}
            </button>
          </div>
          <div className="learning-stats">
            <div className="stat-item">
              <span className="stat-label">New Samples</span>
              <span className="stat-value">
                {learningStats.new_samples_collected} / {learningStats.min_samples_for_retrain}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Progress</span>
              <div className="learning-progress-bar">
                <div
                  className="learning-progress-fill"
                  style={{ width: `${Math.min(100, learningStats.progress_percentage)}%` }}
                ></div>
              </div>
              <span className="stat-value">{learningStats.progress_percentage.toFixed(0)}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Status</span>
              <span className={`stat-badge ${learningStats.ready_for_retrain ? 'ready' : 'collecting'}`}>
                {learningStats.ready_for_retrain ? '✅ Ready' : '📊 Collecting'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="charts-container">
        {/* Income vs Expense Chart */}
        <div className="chart-card">
          <h3>Income vs Expense</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={summaryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                {summaryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category Breakdown Pie Chart */}
        <div className="chart-card">
          <h3>Expense Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => formatCurrency(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Details Table */}
      <div className="category-table-card">
        <h3>Category Details</h3>
        <div className="category-table">
          <div className="table-header">
            <div className="table-cell">Category</div>
            <div className="table-cell">Amount</div>
            <div className="table-cell">Percentage</div>
          </div>
          {categoryData
            .sort((a, b) => b.value - a.value)
            .map((category, index) => {
              const percentage = (category.value / expense) * 100;
              return (
                <div key={category.name} className="table-row">
                  <div className="table-cell">
                    <span
                      className="category-color"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></span>
                    {category.name}
                  </div>
                  <div className="table-cell">{formatCurrency(category.value)}</div>
                  <div className="table-cell">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${percentage}%`,
                          backgroundColor: COLORS[index % COLORS.length]
                        }}
                      ></div>
                    </div>
                    <span className="percentage-text">{percentage.toFixed(1)}%</span>
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
