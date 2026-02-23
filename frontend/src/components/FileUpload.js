import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUpload.css';

function FileUpload({ onFileUpload, error }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/pdf': ['.pdf']
    },
    multiple: false,
    maxSize: 10485760 // 10MB
  });

  return (
    <div className="file-upload-container">
      <div className="upload-section">
        <h2>Upload Your Bank Statement</h2>
        <p className="upload-description">
          Upload your bank statement file for AI-powered analysis
        </p>

        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="dropzone-content">
            <svg
              className="upload-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            {isDragActive ? (
              <p className="dropzone-text">Drop your file here...</p>
            ) : (
              <>
                <p className="dropzone-text">
                  Drag & drop your file here
                </p>
                <p className="dropzone-subtext">or click to browse</p>
              </>
            )}
          </div>
        </div>

        <div className="file-info">
          <p className="supported-formats">
            <strong>Supported formats:</strong> CSV, Excel (.xlsx, .xls), PDF
          </p>
          <p className="file-size-limit">
            <strong>Maximum file size:</strong> 10 MB
          </p>
        </div>

        {error && (
          <div className="error-message">
            <svg
              className="error-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <div className="features-list">
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <div>
              <strong>AI-Powered Classification</strong>
              <p>Automatic categorization using machine learning</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <div>
              <strong>Interactive Dashboard</strong>
              <p>Visual charts and detailed insights</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">💡</span>
            <div>
              <strong>Investment Advice</strong>
              <p>Personalized recommendations based on your finances</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔒</span>
            <div>
              <strong>Secure & Private</strong>
              <p>Your data is processed locally and never stored</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;
