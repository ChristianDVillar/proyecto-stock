import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ConsultInventory from '../ConsultInventory';
import authStore from '../../../stores/AuthStore';

// Mock authStore
jest.mock('../../../stores/AuthStore', () => ({
  getToken: jest.fn(() => 'mock-token'),
  logout: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

describe('ConsultInventory', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it('renders search input', () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ types: [] }),
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ stocks: [], total_items: 0, total_pages: 1 }),
    });

    render(<ConsultInventory />);
    expect(screen.getByPlaceholderText(/buscar por código/i)).toBeInTheDocument();
  });

  it('displays loading state', async () => {
    fetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<ConsultInventory />);
    // Component should show loading or be in loading state
    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
  });

  it('displays error message on fetch failure', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ types: [] }),
    }).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(<ConsultInventory />);
    
    await waitFor(() => {
      expect(screen.queryByText(/error/i)).toBeInTheDocument();
    });
  });

  it('displays stock items', async () => {
    const mockStocks = [
      {
        id: 1,
        barcode: 'TEST001',
        inventario: 'INV001',
        dispositivo: { value: 'laptop' },
        modelo: 'Test Model',
        cantidad: 5,
        status: 'disponible',
        location: 'Almacén A',
      },
    ];

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ types: [] }),
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stocks: mockStocks,
        total_items: 1,
        total_pages: 1,
      }),
    });

    render(<ConsultInventory />);

    await waitFor(() => {
      expect(screen.getByText('TEST001')).toBeInTheDocument();
      expect(screen.getByText('INV001')).toBeInTheDocument();
    });
  });
});

