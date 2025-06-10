import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import NewInventory from './components/NewInventory';
import ConsultInventory from './components/ConsultInventory';
import UserDashboard from './components/UserDashboard';
import Login from './components/Login';
import Footer from './components/Footer';
import authStore from './services/AuthStore';
import { getRouteByPath, canAccessRoute } from './utils/routes';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentView, setCurrentView] = useState('nuevo-inventario');
  const [isAdmin, setIsAdmin] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Efecto para manejar la autenticación
  useEffect(() => {
    const initAuth = async () => {
      try {
        setIsLoading(true);
        // Intentar inicializar desde localStorage
        await authStore.initializeFromStorage();
        
        // Verificar el estado de autenticación
        const loggedIn = authStore.isLoggedIn();
        const admin = authStore.isAdmin();
        const userType = authStore.getUserType();
        
        console.log('App initialization:', {
          loggedIn,
          admin,
          userType,
          token: !!authStore.getToken(),
          storage: {
            token: !!localStorage.getItem('jwt_token'),
            username: localStorage.getItem('username'),
            userType: localStorage.getItem('user_type')
          }
        });

        setIsLoggedIn(loggedIn);
        setIsAdmin(admin);
        setIsInitialized(true);

        // Determinar la vista inicial basada en la URL
        const currentPath = window.location.pathname;
        const route = getRouteByPath(currentPath);
        
        // Solo redirigir si estamos en una ruta protegida y no estamos autenticados
        if (route.requiresAuth && !loggedIn && currentPath !== '/login') {
          window.location.replace('/login');
          return;
        }
        
        // Si estamos en login y ya estamos autenticados, redirigir a home
        if (currentPath === '/login' && loggedIn) {
          window.location.replace('/');
          return;
        }
        
        setCurrentView(route.view);
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
      try {
        const { detail } = event;
        const loggedIn = detail.isLoggedIn;
        const admin = authStore.isAdmin();
        
        console.log('Auth state changed:', {
          loggedIn,
          admin,
          userType: authStore.getUserType(),
          token: !!authStore.getToken()
        });

        setIsLoggedIn(loggedIn);
        setIsAdmin(admin);

        // Solo redirigir si el estado de autenticación cambió
        const currentPath = window.location.pathname;
        const route = getRouteByPath(currentPath);
        
        if (route.requiresAuth && !loggedIn && currentPath !== '/login') {
          window.location.replace('/login');
        }
      } catch (error) {
        console.error('Error handling auth change:', error);
      }
    };

    // Suscribirse a cambios en el estado de autenticación
    authStore.addEventListener('change', handleAuthChange);
    
    // Verificar el token periódicamente
    const tokenCheckInterval = setInterval(async () => {
      if (authStore.getToken()) {
        const isValid = await authStore.verifyToken();
        if (!isValid && window.location.pathname !== '/login') {
          console.log('Token verification failed during interval check');
          setIsLoggedIn(false);
          setIsAdmin(false);
          window.location.replace('/login');
        }
      }
    }, 60000); // Verificar cada minuto

    return () => {
      authStore.removeEventListener('change', handleAuthChange);
      clearInterval(tokenCheckInterval);
    };
  }, []);

  // Mostrar pantalla de carga mientras se inicializa
  if (isLoading) {
    return (
      <div className="App">
        <div className="loading-screen">
          <h2>Cargando...</h2>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    const currentPath = window.location.pathname;
    const route = getRouteByPath(currentPath);
    
    // Si estamos en /login, siempre mostrar el componente Login
    if (currentPath === '/login') {
      return <Login />;
    }
    
    // Para otras rutas, verificar la autenticación
    if (!canAccessRoute(route, isLoggedIn, isAdmin)) {
      return <Login />;
    }

    switch (currentView) {
      case 'consultar':
        return <ConsultInventory />;
      case 'usuarios':
        return isAdmin ? <UserDashboard /> : <div>No autorizado</div>;
      case 'nuevo-inventario':
      default:
        return <NewInventory />;
    }
  };

  return (
    <div className="App">
      {isLoggedIn && <Header onNavigate={setCurrentView} isAdmin={isAdmin} />}
      <main className="App-main">
        {renderContent()}
      </main>
      <Footer />
    </div>
  );
}

export default App;
