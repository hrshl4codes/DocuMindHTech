import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import LandingView from './components/LandingView';
import UploadView from './components/UploadView';
import QueryView from './components/QueryView';
import './App.css';

const API_BASE_URL =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? ''
    : 'https://documindrex.onrender.com');

export default function App() {
  const [view, setView] = useState('landing');
  const [transitionClass, setTransitionClass] = useState('visible');
  const [documentId, setDocumentId] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const [conversation, setConversation] = useState([]);
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const transitionTimeout = useRef(null);

  useEffect(() => () => clearTimeout(transitionTimeout.current), []);

  const transitionTo = (nextView) => {
    clearTimeout(transitionTimeout.current);
    setTransitionClass('exiting');
    transitionTimeout.current = setTimeout(() => {
      setView(nextView);
      setTransitionClass('entering');
      requestAnimationFrame(() => {
        requestAnimationFrame(() => setTransitionClass('visible'));
      });
    }, 300);
  };

  const handleUpload = async (file, text) => {
    if (loading) return;
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      } else {
        formData.append('text', text);
      }
      const res = await axios.post(`${API_BASE_URL}/api/upload`, formData);
      if (res.data.success) {
        setDocumentId(res.data.document_id);
        setDocumentName(file ? file.name : 'pasted text');
        setConversation([]);
        setCitations([]);
        transitionTo('query');
      } else {
        setError(res.data.error || 'Upload failed');
      }
    } catch (err) {
      setError('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async (question) => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(`${API_BASE_URL}/api/query`, {
        document_id: documentId,
        question,
      });
      if (res.data.success) {
        setConversation((prev) => [...prev, { question, answer: res.data.answer }]);
        if (res.data.citations) setCitations(res.data.citations);
      } else {
        setError(res.data.error || 'Query failed');
      }
    } catch (err) {
      setError('Query failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    clearTimeout(transitionTimeout.current);
    setTransitionClass('exiting');
    transitionTimeout.current = setTimeout(() => {
      setDocumentId(null);
      setDocumentName('');
      setConversation([]);
      setCitations([]);
      setError('');
      setView('upload');
      setTransitionClass('entering');
      requestAnimationFrame(() => {
        requestAnimationFrame(() => setTransitionClass('visible'));
      });
    }, 300);
  };

  if (view === 'landing') {
    return (
      <div className={`app view-wrapper ${transitionClass}`}>
        <LandingView onOpenApp={() => transitionTo('upload')} />
      </div>
    );
  }

  return (
    <div className={`app ${view === 'query' ? 'view-query' : ''}`}>
      <div className="glow-blob glow-blob--upload" />
      <div className="glow-blob glow-blob--query" />
      <div className={`view-wrapper ${transitionClass}`}>
        {view === 'upload' ? (
          <UploadView onUpload={handleUpload} loading={loading} error={error} />
        ) : (
          <QueryView
            documentName={documentName}
            conversation={conversation}
            citations={citations}
            onQuery={handleQuery}
            onReset={handleReset}
            loading={loading}
            error={error}
          />
        )}
      </div>
    </div>
  );
}
