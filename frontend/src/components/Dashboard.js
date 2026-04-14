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
  ResponsiveContainer,
} from 'recharts';
import './Dashboard.css';
import config from '../config';

const COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6',
  '#F43F5E', '#06B6D4', '#EC4899', '#84CC16',
  '#F97316', '#14B8A6',
];

/* ---- Shared chart theme ---- */
const chartTheme = {
  grid: { stroke: 'rgba(255,255,255,0.05)', strokeDasharray: '3 3' },
  axis: {
    tick: { fill: '#64748B', fontSize: 12, fontFamily: 'Inter, sans-serif' },
    axisLine: { stroke: 'rgba(255,255,255,0.06)' },
    tickLine: { stroke: 'transparent' },
  },
  tooltip: {
    contentStyle: {
      backgroundColor: '#0F1624',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '10px',
      color: '#E2E8F0',
      fontSize: '13px',
      fontFamily: 'Inter, sans-serif',
      boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
    },
    labelStyle: { color: '#94A3B8', fontSize: '12px', marginBottom: '4px' },
    cursor: { fill: 'rgba(255,255,255,0.03)' },
  },
};

function Dashboard({ data, onReset, onShowInvestmentAdvice }) {
  const { income, expense, remaining_balance, categories, fileName } = data;
  const [learningStats, setLearningStats] = React.useState(null);
  const [retraining, setRetraining] = React.useState(false);

  React.useEffect(() => {
    fetchLearningStats();
    const interval = setInterval(fetchLearningStats, config.learning.statsRefreshInterval);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
        method: 'POST',
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

  const categoryData = Object.entries(categories).map(([name, value]) => ({
    name,
    value: parseFloat(value),
  }));

  const summaryData = [
    { name: 'Income',  value: parseFloat(income),  color: '#10B981' },
    { name: 'Expense', value: parseFloat(expense), color: '#F43F5E' },
  ];

  const formatCurrency = (value) =>
    `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

  const isPositive = remaining_balance >= 0;

  /* ---- Custom pie label ---- */
  const renderPieLabel = ({ name, percent }) => {
    if (percent < 0.05) return null;
    return `${name} ${(percent * 100).toFixed(0)}%`;
  };

  return (
    <div className="dashboard">
      {/* Hero banner */}
      <div className="dashboard-hero-banner">
        {/* background photo */}
        <img
          src="https://pixabay.com/get/g3fe8265de4cb64390a290e169fbf55c08cdf2a858f4b22276a46a667f23834e234e7e7d8027468b7fd471fda60a89745.jpg"
          alt="technology network background by Developer_Console on Pixabay"
          className="banner-bg-photo"
          aria-hidden="true"
          width="800"
          height="600"
        />
        <div className="banner-left">
          <h2>
            Financial <span>Analysis</span>
          </h2>
          <p className="banner-file-name">📄 {fileName}</p>
        </div>
        <div className="banner-right">
          <button className="btn-invest" onClick={onShowInvestmentAdvice}>
            💡 Invest Advice
          </button>
          <button className="btn-reset" onClick={onReset}>
            ↑ New File
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="summary-cards">
        <div className="summary-card income">
          <div className="card-icon-wrap">💰</div>
          <div className="card-content">
            <p className="card-label">Total Income</p>
            <p className="card-value">{formatCurrency(income)}</p>
          </div>
        </div>

        <div className="summary-card expense">
          <div className="card-icon-wrap">💸</div>
          <div className="card-content">
            <p className="card-label">Total Expense</p>
            <p className="card-value">{formatCurrency(expense)}</p>
          </div>
        </div>

        <div className={`summary-card balance${isPositive ? '' : ' negative'}`}>
          <div className="card-icon-wrap">{isPositive ? '✅' : '⚖️'}</div>
          <div className="card-content">
            <p className="card-label">Net Balance</p>
            <p
              className="card-value"
              style={{ color: isPositive ? 'var(--color-accent-green)' : 'var(--color-accent-red)' }}
            >
              {formatCurrency(remaining_balance)}
            </p>
          </div>
        </div>
      </div>

      {/* AI Learning Progress */}
      {learningStats && (
        <div className="learning-progress-card">
          <div className="learning-header">
            <div className="learning-title-group">
              <h3>🤖 AI Learning Progress</h3>
              <p className="learning-subtitle">
                System learns from every upload to improve accuracy
              </p>
            </div>
            <button
              className={`retrain-button${!learningStats.ready_for_retrain ? ' disabled' : ''}`}
              onClick={handleRetrain}
              disabled={!learningStats.ready_for_retrain || retraining}
            >
              {retraining ? '⏳ Retraining…' : '🔄 Retrain Model'}
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
                />
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

      {/* Charts */}
      <div className="charts-container">
        {/* Bar: Income vs Expense */}
        <div className="chart-card">
          <div className="chart-card-header">
            <h3>Income vs Expense</h3>
            <span className="chart-tag">Overview</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={summaryData} barSize={52}>
              <CartesianGrid {...chartTheme.grid} vertical={false} />
              <XAxis dataKey="name" {...chartTheme.axis} />
              <YAxis
                {...chartTheme.axis}
                tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                width={60}
              />
              <Tooltip
                formatter={(value) => [formatCurrency(value), '']}
                contentStyle={chartTheme.tooltip.contentStyle}
                labelStyle={chartTheme.tooltip.labelStyle}
                cursor={chartTheme.tooltip.cursor}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {summaryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.9} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie: Expense Breakdown */}
        <div className="chart-card">
          <div className="chart-card-header">
            <h3>Expense Breakdown</h3>
            <span className="chart-tag">Categories</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderPieLabel}
                outerRadius={95}
                innerRadius={40}
                dataKey="value"
                paddingAngle={2}
              >
                {categoryData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    fillOpacity={0.88}
                    stroke="transparent"
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [formatCurrency(value), 'Amount']}
                contentStyle={chartTheme.tooltip.contentStyle}
                labelStyle={chartTheme.tooltip.labelStyle}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Table */}
      <div className="category-table-card">
        <div className="category-table-card-header">
          <h3>Category Details</h3>
          <span className="category-count">{categoryData.length} categories</span>
        </div>
        <div className="category-table">
          <div className="table-header">
            <div className="table-cell">Category</div>
            <div className="table-cell">Amount</div>
            <div className="table-cell">Share</div>
          </div>
          {[...categoryData]
            .sort((a, b) => b.value - a.value)
            .map((category, index) => {
              const percentage = (category.value / expense) * 100;
              return (
                <div key={category.name} className="table-row">
                  <div className="table-cell">
                    <span
                      className="category-color"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    />
                    {category.name}
                  </div>
                  <div className="table-cell amount-cell">
                    {formatCurrency(category.value)}
                  </div>
                  <div className="table-cell">
                    <div className="progress-bar-wrap">
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${percentage}%`,
                            backgroundColor: COLORS[index % COLORS.length],
                          }}
                        />
                      </div>
                      <span className="percentage-text">{percentage.toFixed(1)}%</span>
                    </div>
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
