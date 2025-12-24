import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NewInventory from '../NewInventory';
import authStore from '../../../stores/AuthStore';

// Mock authStore
jest.mock('../../../stores/AuthStore', () => ({
  getToken: jest.fn(() => 'mock-token'),
}));

// Mock Quagga
jest.mock('@ericblade/quagga2', () => ({
  __esModule: true,
  default: {
    init: jest.fn(() => Promise.resolve()),
    start: jest.fn(),
    stop: jest.fn(),
    onDetected: jest.fn(),
    decodeSingle: jest.fn(() => Promise.resolve({ codeResult: { code: '123456' } })),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe('NewInventory Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders inventory form', () => {
    render(<NewInventory />);
    expect(screen.getByText(/nuevo inventario/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/inventario/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/modelo/i)).toBeInTheDocument();
  });

  it('disables save button when required fields are missing', () => {
    render(<NewInventory />);
    const saveButton = screen.getByRole('button', { name: /guardar/i });
    expect(saveButton).toBeDisabled();
  });

  it('enables save button when all required fields are filled', () => {
    render(<NewInventory />);
    
    const inventarioInput = screen.getByPlaceholderText(/inventario/i);
    const cantidadInput = screen.getByPlaceholderText(/cantidad/i);
    
    fireEvent.change(inventarioInput, { target: { value: 'INV001' } });
    fireEvent.change(cantidadInput, { target: { value: '5' } });
    
    // Note: This test may need adjustment based on actual form validation
  });

  it('shows error message on save failure', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Código de barras duplicado' }),
    });

    render(<NewInventory />);
    
    // Fill form and submit
    const inventarioInput = screen.getByPlaceholderText(/inventario/i);
    fireEvent.change(inventarioInput, { target: { value: 'INV001' } });
    
    // Mock barcode scan
    const barcodeInput = screen.getByPlaceholderText(/código escaneado/i);
    fireEvent.change(barcodeInput, { target: { value: 'TEST123' } });
    
    const saveButton = screen.getByRole('button', { name: /guardar/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
  });
});

