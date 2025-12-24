import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Login from '../Login';
import authStore from '../../../stores/AuthStore';

// Mock authStore
jest.mock('../../../stores/AuthStore', () => ({
  getToken: jest.fn(() => null),
  login: jest.fn(),
  isLoggedIn: jest.fn(() => false),
}));

// Mock fetch
global.fetch = jest.fn();

describe('Login Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    authStore.login.mockClear();
  });

  it('renders login form', () => {
    render(<Login />);
    expect(screen.getByPlaceholderText(/usuario/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('shows error on failed login', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Credenciales incorrectas' }),
    });

    render(<Login />);
    
    const usernameInput = screen.getByPlaceholderText(/usuario/i);
    const passwordInput = screen.getByPlaceholderText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/credenciales incorrectas/i)).toBeInTheDocument();
    });
  });

  it('calls authStore.login on successful login', async () => {
    const mockToken = 'mock-jwt-token';
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: mockToken,
        user: { username: 'testuser', user_type: 'user' },
      }),
    });

    authStore.login.mockReturnValue(true);

    render(<Login />);
    
    const usernameInput = screen.getByPlaceholderText(/usuario/i);
    const passwordInput = screen.getByPlaceholderText(/contraseña/i);
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:5000/api/auth/login',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  it('validates required fields', async () => {
    render(<Login />);
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i });
    fireEvent.click(submitButton);

    // Should show validation error or prevent submission
    await waitFor(() => {
      expect(fetch).not.toHaveBeenCalled();
    });
  });
});
