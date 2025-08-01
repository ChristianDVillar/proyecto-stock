import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './assets/styles/base.css';
import './assets/styles/components.css';
import Header from './components/Header';
import NewInventory from './components/NewInventory';
import ConsultInventory from './components/ConsultInventory';
import UserDashboard from './components/UserDashboard';
import Login from './components/Login';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import authStore from './services/AuthStore';
import { getRouteByPath, getRouteByView, canAccessRoute } from './utils/routes';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        setIsLoading(true);
        await authStore.initializeFromStorage();
        
        const loggedIn = authStore.isLoggedIn();
        const admin = authStore.isAdmin();
        
        setIsLoggedIn(loggedIn);
        setIsAdmin(admin);
        setIsInitialized(true);
      } catch (error) {
        console.error('Error during initialization:', error);
        setIsLoggedIn(false);
        setIsAdmin(false);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();

    const handleAuthChange = (event) => {
      const { detail } = event;
      setIsLoggedIn(detail.isLoggedIn);
      setIsAdmin(authStore.isAdmin());
    };

    authStore.addEventListener('change', handleAuthChange);
    
    return () => {
      authStore.removeEventListener('change', handleAuthChange);
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
    <Router>
      <div className="App">
        <ErrorBoundary>
          <Header isLoggedIn={isLoggedIn} isAdmin={isAdmin} />
          <main className="main-content">
            <Routes>
              <Route 
                path="/login" 
                element={
                  isLoggedIn ? (
                    <Navigate to={isAdmin ? "/admin" : "/"} replace />
                  ) : (
                    <Login />
                  )
                } 
              />
              <Route 
                path="/nuevo-inventario" 
                element={
                  isLoggedIn ? (
                    <NewInventory />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                } 
              />
              <Route 
                path="/consultar-inventario" 
                element={
                  isLoggedIn ? (
                    <ConsultInventory />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                } 
              />
              <Route 
                path="/admin" 
                element={
                  isLoggedIn && isAdmin ? (
                    <UserDashboard />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                } 
              />
              <Route 
                path="/" 
                element={
                  isLoggedIn ? (
                    <Navigate to="/nuevo-inventario" replace />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                } 
              />
            </Routes>
          </main>
          <Footer />
        </ErrorBoundary>
      </div>
    </Router>
  );
}

export default App;
