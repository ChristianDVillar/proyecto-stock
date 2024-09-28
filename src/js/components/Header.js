import React, { useState, useEffect } from 'react';
import authStore from '../../stores/AuthStore'; // Asegúrate de que la ruta sea correcta

const Header = () => {
    const [userName, setUserName] = useState(authStore.getUserName());
    const [showDropdown, setShowDropdown] = useState(false);

    useEffect(() => {
        const handleAuthChange = () => {
            setUserName(authStore.getUserName());
        };

        authStore.on('change', handleAuthChange);

        return () => {
            authStore.removeListener('change', handleAuthChange);
        };
    }, []);

    const handleLogout = () => {
        authStore.logout();
        setShowDropdown(false); // Cerrar el dropdown al cerrar sesión
    };

    return (
        <header className="header">
            <div className="logo">Control de Stock</div>
            <nav className="nav">
                <a href="#nuevo-inventario">Nuevo Inventario</a>
                <a href="#consultar">Consultar Inventario</a>
                <a href="mailto:christianvillar@live.com.ar" id="contact-link">Contacto</a>
                <div className="date-time">{new Date().toLocaleString()}</div>
                {userName && (
                    <div className="user-menu">
                    <span 
                        className="user-name" 
                        onClick={() => setShowDropdown(!showDropdown)}
                        style={{ cursor: 'pointer' }}
                    >
                        {userName}
                    </span>
                    {showDropdown && (
                        <div className="dropdown-menu">
                            <ul>
                                <li><a onClick={handleLogout}>Cerrar Sesión</a></li>
                                <li><a href="#profile">Perfil</a></li>
                            </ul>
                        </div>
                    )}
                </div>
                )}
            </nav>
        </header>
    );
};

export default Header;
