import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Header from './js/components/Header';
import NewInventory from './js/components/NewInventory';
import ConsultInventory from './js/components/ConsultInventory';
import SolicitarElementos from './js/components/SolicitarElementos';
import UserDashboard from './js/components/UserDashboard';
import Dashboard from './js/components/Dashboard';
import Suppliers from './js/components/Suppliers';
import PurchaseOrders from './js/components/PurchaseOrders';
import Warehouses from './js/components/Warehouses';
import Transfers from './js/components/Transfers';
import QuickScan from './js/components/QuickScan';
import AlertSettings from './js/components/AlertSettings';
import CyclicInventory from './js/components/CyclicInventory';
import BillingPlans from './js/components/BillingPlans';
import Integrations from './js/components/Integrations';
import Portal from './js/components/Portal';
import PublicProduct from './js/components/PublicProduct';
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
            <Route path="/p/:token" element={<PublicProduct />} />
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
              path="/dashboard"
              element={
                <ProtectedRoute adminOnly>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/proveedores"
              element={
                <ProtectedRoute adminOnly>
                  <Suppliers />
                </ProtectedRoute>
              }
            />
            <Route
              path="/ordenes-compra"
              element={
                <ProtectedRoute adminOnly>
                  <PurchaseOrders />
                </ProtectedRoute>
              }
            />
            <Route
              path="/almacenes"
              element={
                <ProtectedRoute adminOnly>
                  <Warehouses />
                </ProtectedRoute>
              }
            />
            <Route
              path="/transferencias"
              element={
                <ProtectedRoute adminOnly>
                  <Transfers />
                </ProtectedRoute>
              }
            />
            <Route path="/escaneo" element={<ProtectedRoute adminOnly><QuickScan /></ProtectedRoute>} />
            <Route path="/alertas" element={<ProtectedRoute adminOnly><AlertSettings /></ProtectedRoute>} />
            <Route path="/inventario-ciclico" element={<ProtectedRoute adminOnly><CyclicInventory /></ProtectedRoute>} />
            <Route path="/planes" element={<ProtectedRoute adminOnly><BillingPlans /></ProtectedRoute>} />
            <Route path="/integraciones" element={<ProtectedRoute adminOnly><Integrations /></ProtectedRoute>} />
            <Route path="/portal" element={<ProtectedRoute><Portal /></ProtectedRoute>} />
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
