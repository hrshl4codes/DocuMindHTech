import React, { useState } from 'react';
import { Upload, MessageSquare, FileText, Brain, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';
import './App.css';

function App() {
  const [currentDocument, setCurrentDocument] = useState(null);
  const [currentDocumentId, setCurrentDocumentId] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [fileInfo, setFileInfo] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://documindrex.onrender.com';

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCurrentDocument(file);
      setFileInfo({
        name: file.name,
        size: formatFileSize(file.size),
        type: file.type
      });
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      setCurrentDocument(file);
      setFileInfo({
        name: file.name,
        size: formatFileSize(file.size),
        type: file.type
      });
    }
  };

  const handleUpload = async () => {
    if (!currentDocument && !textInput.trim()) {
      setError('Please select a file or enter text');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      if (currentDocument) {
        formData.append('file', currentDocument);
      } else {
        formData.append('text', textInput);
      }

      const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setCurrentDocumentId(response.data.document_id);
        setSuccess('Document uploaded successfully!');
      } else {
        setError(response.data.error || 'Upload failed');
      }
    } catch (error) {
      setError('Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    if (!currentDocumentId) {
      setError('Please upload a document first');
      return;
    }

    setLoading(true);
    setError('');
    setAnswer('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/query`, {
        document_id: currentDocumentId,
        question: question
      });

      if (response.data.success) {
        setAnswer(response.data.answer);
      } else {
        setError(response.data.error || 'Query failed');
      }
    } catch (error) {
      setError('Query failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setCurrentDocument(null);
    setCurrentDocumentId(null);
    setTextInput('');
    setQuestion('');
    setAnswer('');
    setFileInfo(null);
    setError('');
    setSuccess('');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="App">
      <div className="container">
        <div className="header">
          <h1><Brain className="header-icon" /> DocuMind AI</h1>
          <p>Professional Document Intelligence System</p>
        </div>

        <div className="main-content">
          <div className="section">
            <h2 className="section-title">
              <Upload size={20} /> Document Upload
            </h2>
            
            <div 
              className="upload-area"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('fileInput').click()}
            >
              <div className="upload-icon">📁</div>
              <div className="upload-text">
                <strong>Click to upload</strong> or drag and drop<br />
                <small>Supports PDF, DOCX, TXT, and more</small>
              </div>
            </div>
            
            <input
              type="file"
              id="fileInput"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.txt,.md"
            />
            
            {fileInfo && (
              <div className="file-info">
                <div className="file-name">{fileInfo.name}</div>
                <div className="file-size">{fileInfo.size}</div>
              </div>
            )}

            <div className="section-title">
              <FileText size={20} /> Or Paste Text
            </div>
            <textarea
              className="text-input"
              placeholder="Paste your document text here..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
            />
            
            <button className="btn" onClick={handleUpload} disabled={loading}>
              {loading ? 'Uploading...' : 'Upload Document'}
            </button>
            <button className="btn btn-secondary" onClick={handleClear}>
              Clear
            </button>
          </div>

          <div className="section">
            <h2 className="section-title">
              <MessageSquare size={20} /> Ask Questions
            </h2>
            
            <input
              type="text"
              className="query-input"
              placeholder="What would you like to know about the document?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            
            <button className="btn" onClick={handleQuery} disabled={loading || !currentDocumentId}>
              {loading ? 'Processing...' : 'Ask Question'}
            </button>
            <button className="btn btn-secondary" onClick={() => setQuestion('')}>
              Clear Query
            </button>
            
            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <div>Processing your request...</div>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="error">
            <AlertCircle size={20} style={{ marginRight: '10px', verticalAlign: 'middle' }} />
            {error}
          </div>
        )}

        {success && (
          <div className="success">
            <CheckCircle size={20} style={{ marginRight: '10px', verticalAlign: 'middle' }} />
            {success}
          </div>
        )}

        {answer && (
          <div className="results-section">
            <h2 className="section-title">
              <Brain size={20} /> Answer
            </h2>
            <div className="answer">
              <div className="answer-text">{answer}</div>
            </div>
          </div>
        )}

        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">✅</div>
            <div className="stat-label">System Running</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">React</div>
            <div className="stat-label">Frontend</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">Ready</div>
            <div className="stat-label">Status</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">API</div>
            <div className="stat-label">Connected</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
