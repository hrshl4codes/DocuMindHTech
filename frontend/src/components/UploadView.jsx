import React, { useState, useRef } from 'react';
import './UploadView.css';

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default function UploadView({ onUpload, loading, error }) {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [dragover, setDragover] = useState(false);
  const [textFocused, setTextFocused] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => { e.preventDefault(); setDragover(true); };
  const handleDragLeave = () => setDragover(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setDragover(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.size > 0) setFile(dropped);
  };
  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.size > 0) setFile(selected);
  };

  const canUpload = (file || text.trim()) && !loading;

  return (
    <div className="upload-view">
      <span className="upload-view__wordmark">DocuMind</span>

      <div className="upload-view__content">
        <h1 className="upload-view__heading">
          Drop a document.<br />
          <span className="upload-view__heading--accent">Ask anything.</span>
        </h1>

        <div
          role="button"
          tabIndex={0}
          aria-label="File drop zone"
          className={[
            'upload-view__dropzone',
            dragover ? 'upload-view__dropzone--dragover' : '',
            file ? 'upload-view__dropzone--filled' : '',
          ].join(' ')}
          onClick={() => fileInputRef.current.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current.click();
            }
          }}
        >
          <span className="upload-view__corner upload-view__corner--tl" />
          <span className="upload-view__corner upload-view__corner--tr" />
          <span className="upload-view__corner upload-view__corner--bl" />
          <span className="upload-view__corner upload-view__corner--br" />

          {file ? (
            <div className="upload-view__file-info">
              <span className="upload-view__file-name">{file.name}</span>
              <span className="upload-view__file-size">{formatFileSize(file.size)}</span>
            </div>
          ) : (
            <>
              <div className="upload-view__dropzone-icon">↑</div>
              <p className="upload-view__dropzone-text">drag & drop or click to upload</p>
              <p className="upload-view__dropzone-types">PDF · DOCX · TXT · MD</p>
            </>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />

        <p className="upload-view__divider">or paste text below</p>

        <textarea
          className="upload-view__textarea"
          placeholder="Paste your document text here..."
          value={text}
          rows={textFocused || text ? 3 : 1}
          onFocus={() => setTextFocused(true)}
          onBlur={() => setTextFocused(!!text)}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          className="upload-view__submit"
          onClick={() => {
            if (!canUpload) return;
            onUpload(file, text);
          }}
          disabled={!canUpload}
        >
          {loading ? 'Uploading…' : 'Upload'}
        </button>

        {error && <p className="upload-view__error">{error}</p>}
      </div>
    </div>
  );
}
