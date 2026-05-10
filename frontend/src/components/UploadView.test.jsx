import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import UploadView from './UploadView';

const noop = () => {};

test('renders wordmark', () => {
  render(<UploadView onUpload={noop} loading={false} error="" />);
  expect(screen.getByText('DocuMind')).toBeInTheDocument();
});

test('renders heading', () => {
  render(<UploadView onUpload={noop} loading={false} error="" />);
  expect(screen.getByText(/Drop a document/i)).toBeInTheDocument();
  expect(screen.getByText(/Ask anything/i)).toBeInTheDocument();
});

test('upload button is disabled with no input', () => {
  render(<UploadView onUpload={noop} loading={false} error="" />);
  expect(screen.getByRole('button', { name: /upload/i })).toBeDisabled();
});

test('upload button calls onUpload when text is provided', () => {
  const onUpload = jest.fn();
  render(<UploadView onUpload={onUpload} loading={false} error="" />);
  fireEvent.change(screen.getByPlaceholderText(/Paste your document/i), {
    target: { value: 'some document text' }
  });
  fireEvent.click(screen.getByRole('button', { name: /upload/i }));
  expect(onUpload).toHaveBeenCalledWith(null, 'some document text');
});

test('shows error message when error prop is set', () => {
  render(<UploadView onUpload={noop} loading={false} error="Upload failed" />);
  expect(screen.getByText('Upload failed')).toBeInTheDocument();
});

test('shows Uploading… text when loading', () => {
  render(<UploadView onUpload={noop} loading={true} error="" />);
  expect(screen.getByRole('button', { name: /uploading/i })).toBeInTheDocument();
});
