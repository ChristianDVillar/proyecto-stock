import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Header from './js/components/Header';
import NewInventory from './js/components/NewInventory';
import ConsultInventory from './js/components/ConsultInventory';
import SolicitarElementos from './js/components/SolicitarElementos';
import UserDashboard from './js/components/UserDashboard';
import Login from './js/components/Login';
import Footer from './js/components/Footer';
import ProtectedRoute from './js/components/ProtectedRoute';
import authStore from './stores/AuthStore';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        setIsLoading(true);
        await authStore.initializeFromStorage();
        setIsLoggedIn(authStore.validateAuth());
        setIsAdmin(authStore.isAdmin());
      } catch (error) {
        setIsLoggedIn(false);
        setIsAdmin(false);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();

    const handleAuthChange = () => {
      setIsLoggedIn(authStore.validateAuth());
      setIsAdmin(authStore.isAdmin());
    };
    authStore.on('change', handleAuthChange);

    const tokenCheckInterval = setInterval(async () => {
      if (authStore.getToken()) {
        const isValid = await authStore.verifyToken();
        if (!isValid) {
          setIsLoggedIn(false);
          setIsAdmin(false);
        }
      }
    }, 60000);

    return () => {
      authStore.removeListener('change', handleAuthChange);
      clearInterval(tokenCheckInterval);
    };
  }, []);

  if (isLoading) {
    return (
      <div className="App">
        <div className="loading-screen">
          <h2>Cargando...</h2>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        {isLoggedIn && <Header isAdmin={isAdmin} />}
        <main className="App-main">
          <Routes>
            <Route path="/login" element={isLoggedIn ? <Navigate to="/" replace /> : <Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute adminOnly>
                  <NewInventory />
                </ProtectedRoute>
              }
            />
            <Route
              path="/consultar"
              element={
                <ProtectedRoute adminOnly>
                  <ConsultInventory />
                </ProtectedRoute>
              }
            />
            <Route
              path="/solicitar"
              element={
                <ProtectedRoute>
                  <SolicitarElementos />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin>
                  <UserDashboard />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/solicitar" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
