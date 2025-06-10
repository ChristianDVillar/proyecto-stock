import React, { useState, useEffect } from 'react';
import authStore from '../../stores/AuthStore';
import '../../styles/Header.css';

const Header = ({ onNavigate, isAdmin }) => {
    const [userName, setUserName] = useState(authStore.getUserName());
    const [showDropdown, setShowDropdown] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const handleAuthChange = () => {
            setUserName(authStore.getUserName());
        };

        authStore.on('change', handleAuthChange);

        // Actualizar la hora cada segundo
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => {
            authStore.removeListener('change', handleAuthChange);
            clearInterval(timer);
        };
    }, []);

    const handleLogout = () => {
        authStore.logout();
        setShowDropdown(false);
    };

    const handleNavigation = (view) => {
        onNavigate(view);
        setShowDropdown(false);
    };

    return (
        <header className="header">
            <div className="logo">Control de Stock</div>
            <nav className="nav">
                <button 
                    className="nav-button" 
                    onClick={() => handleNavigation('nuevo-inventario')}
                >
                    Nuevo Inventario
                </button>
                <button 
                    className="nav-button" 
                    onClick={() => handleNavigation('consultar')}
                >
                    Consultar Inventario
                </button>
                {isAdmin && (
                    <button 
                        className="nav-button" 
                        onClick={() => handleNavigation('usuarios')}
                    >
                        Gestión de Usuarios
                    </button>
                )}
                <a href="mailto:christianvillar@live.com.ar" className="nav-button">
                    Contacto
                </a>
                <div className="date-time">
                    {currentTime.toLocaleString()}
                </div>
                <div className="user-menu">
                    <button 
                        className="user-button"
                        onClick={() => setShowDropdown(!showDropdown)}
                    >
                        {userName}
                    </button>
                    {showDropdown && (
                        <div className="dropdown-menu">
                            {isAdmin && (
                                <button 
                                    className="admin-option"
                                    onClick={() => handleNavigation('usuarios')}
                                >
                                    Gestión de Usuarios
                                </button>
                            )}
                            <button onClick={() => handleNavigation('profile')}>Mi Perfil</button>
                            <button onClick={handleLogout}>Cerrar Sesión</button>
                        </div>
                    )}
                </div>
            </nav>
        </header>
    );
};

export default Header;
