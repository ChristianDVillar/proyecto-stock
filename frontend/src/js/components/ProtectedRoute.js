import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import authStore from '../../stores/AuthStore';

/**
 * Ruta protegida: redirige a /login si no hay sesión.
 * requireAdmin: solo admin; si no, redirige a /solicitar.
 * adminOnly: igual que requireAdmin (solo admin puede ver la ruta).
 */
export default function ProtectedRoute({ children, requireAdmin = false, adminOnly = false }) {
  const location = useLocation();
  const isLoggedIn = authStore.validateAuth();
  const isAdmin = authStore.isAdmin();
  const mustBeAdmin = requireAdmin || adminOnly;

  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (mustBeAdmin && !isAdmin) {
    return <Navigate to="/solicitar" replace />;
  }
  return children;
}
