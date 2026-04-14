import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

/* ---- Right panel stats ---- */
const heroStats = [
  { value: '99.2%', label: 'Accuracy' },
  { value: '<2s',   label: 'Analysis' },
  { value: '50+',   label: 'Categories' },
];

/* ---- Steps ---- */
const steps = [
  { icon: '📤', title: 'Upload Statement', desc: 'CSV, Excel or PDF bank statement' },
  { icon: '🤖', title: 'AI Classifies',   desc: 'ML model categorizes every transaction' },
  { icon: '📊', title: 'View Insights',   desc: 'Interactive charts & investment tips' },
];

/* ---- Feature cards ---- */
const features = [
  { icon: '🤖', colorClass: 'blue',   title: 'AI Classification',  desc: 'Auto-categorization using machine learning' },
  { icon: '📊', colorClass: 'green',  title: 'Interactive Charts', desc: 'Visual charts and detailed insights' },
  { icon: '💡', colorClass: 'gold',   title: 'Investment Advice',  desc: 'Personalized recommendations based on your data' },
  { icon: '🔒', colorClass: 'purple', title: 'Secure & Private',   desc: 'Data processed locally, never stored' },
];

function FileUpload({ onFileUpload, error }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) onFileUpload(acceptedFiles[0]);
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/pdf': ['.pdf'],
    },
    multiple: false,
    maxSize: 10485760,
  });

  return (
    <div className="file-upload-hero">
      {/* ── Left panel: form ── */}
      <div className="upload-left">
        <div className="upload-section">
          <div className="upload-header">
            <h2>Upload Your Bank Statement</h2>
            <p className="upload-description">
              Upload your bank statement file for AI-powered analysis
            </p>
          </div>

          <div {...getRootProps()} className={`dropzone${isDragActive ? ' active' : ''}`}>
            <input {...getInputProps()} />
            <div className="dropzone-content">
              <div className="upload-icon-wrap">
                <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              {isDragActive ? (
                <p className="dropzone-active-text">Drop your file here…</p>
              ) : (
                <>
                  <p className="dropzone-text">Drag & drop your file here</p>
                  <p className="dropzone-subtext">or click to browse files</p>
                </>
              )}
            </div>
          </div>

          <div className="file-info">
            <div className="file-info-item">
              <strong>Formats:</strong> CSV, Excel (.xlsx, .xls), PDF
            </div>
            <div className="file-info-dot" />
            <div className="file-info-item">
              <strong>Max size:</strong> 10 MB
            </div>
          </div>

          {error && (
            <div className="error-message">
              <svg className="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="features-list">
            {features.map((f) => (
              <div key={f.title} className="feature-item">
                <div className={`feature-icon-wrap ${f.colorClass}`}>{f.icon}</div>
                <div className="feature-text">
                  <strong>{f.title}</strong>
                  <p>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right panel: hero visual ── */}
      <div className="upload-right">
        {/* Decorative glow orb */}
        <div className="hero-orb hero-orb-1" aria-hidden="true" />
        <div className="hero-orb hero-orb-2" aria-hidden="true" />

        {/* Hero image — wrapped in browser-mockup frame */}
        <div className="hero-illustration-wrap">
          <div className="hero-illustration-frame">
            <img
              src="https://pixabay.com/get/g603b3949a6f13aefcdf0440a5667a3eac3d396fb1082520f83101fdcee95cc4907fe83e7bf7b0cfd4d9da8af2efcced8.svg"
              alt="Financial analytics dashboard illustration by tanrıca on Pixabay"
              className="hero-illustration"
              width="420"
              height="280"
            />
          </div>
        </div>

        {/* Hero copy */}
        <div className="hero-copy">
          <div className="hero-badge">AI-Powered Finance</div>
          <h3 className="hero-heading">
            Turn raw transactions into<br />
            <span className="hero-heading-accent">actionable insights</span>
          </h3>
          <p className="hero-sub">
            Upload any bank statement and let our ML model classify, analyse, and advise on your finances — in seconds.
          </p>
        </div>

        {/* Stats row */}
        <div className="hero-stats">
          {heroStats.map((s) => (
            <div key={s.label} className="hero-stat">
              <span className="hero-stat-value">{s.value}</span>
              <span className="hero-stat-label">{s.label}</span>
            </div>
          ))}
        </div>

        {/* Steps */}
        <div className="hero-steps">
          {steps.map((s, i) => (
            <div key={s.title} className="hero-step">
              <div className="hero-step-num">{i + 1}</div>
              <div className="hero-step-icon">{s.icon}</div>
              <div className="hero-step-text">
                <strong>{s.title}</strong>
                <span>{s.desc}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Background network photo (decorative) */}
        <img
          src="https://pixabay.com/get/g3fe8265de4cb64390a290e169fbf55c08cdf2a858f4b22276a46a667f23834e234e7e7d8027468b7fd471fda60a89745.jpg"
          alt="technology network background by Developer_Console on Pixabay"
          className="hero-bg-photo"
          aria-hidden="true"
          width="800"
          height="600"
        />
      </div>
    </div>
  );
}

export default FileUpload;
