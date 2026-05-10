import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import QueryView from './QueryView';

const noop = () => {};
const defaultProps = {
  documentName: 'report.pdf',
  conversation: [],
  citations: [],
  onQuery: noop,
  onReset: noop,
  loading: false,
  error: '',
};

test('renders top bar with document name', () => {
  render(<QueryView {...defaultProps} />);
  expect(screen.getByText('report.pdf')).toBeInTheDocument();
  expect(screen.getByText('DocuMind')).toBeInTheDocument();
});

test('renders empty state message', () => {
  render(<QueryView {...defaultProps} />);
  expect(screen.getByText(/Ask a question about your document/i)).toBeInTheDocument();
});

test('renders conversation entries', () => {
  const conversation = [
    { question: 'What is this?', answer: 'It is a test document.' }
  ];
  render(<QueryView {...defaultProps} conversation={conversation} />);
  expect(screen.getByText('What is this?')).toBeInTheDocument();
  expect(screen.getByText('It is a test document.')).toBeInTheDocument();
});

test('citations panel is hidden with no citations', () => {
  const { container } = render(<QueryView {...defaultProps} />);
  const panel = container.querySelector('.query-view__citations');
  expect(panel).not.toHaveClass('query-view__citations--visible');
});

test('citations panel is visible when citations exist', () => {
  const citations = [{ text: 'Some source text here.', source: 'report.pdf', section: 'p1', position: '1' }];
  const { container } = render(<QueryView {...defaultProps} citations={citations} />);
  const panel = container.querySelector('.query-view__citations');
  expect(panel).toHaveClass('query-view__citations--visible');
});

test('calls onQuery when Ask button is clicked with a question', () => {
  const onQuery = jest.fn();
  render(<QueryView {...defaultProps} onQuery={onQuery} />);
  fireEvent.change(screen.getByPlaceholderText(/Ask a question/i), {
    target: { value: 'Who wrote this?' }
  });
  fireEvent.click(screen.getByRole('button', { name: /ask/i }));
  expect(onQuery).toHaveBeenCalledWith('Who wrote this?');
});

test('calls onReset when New document is clicked', () => {
  const onReset = jest.fn();
  render(<QueryView {...defaultProps} onReset={onReset} />);
  fireEvent.click(screen.getByRole('button', { name: /New document/i }));
  expect(onReset).toHaveBeenCalled();
});

test('truncates document name longer than 20 chars', () => {
  render(<QueryView {...defaultProps} documentName="a_very_long_filename_that_exceeds_limit.pdf" />);
  expect(screen.getByText('a_very_long_filename…')).toBeInTheDocument();
});
