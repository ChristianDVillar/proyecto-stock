import React, { useState, useEffect } from 'react';
import authStore from '../../stores/AuthStore.js'; // Asegúrate de que la ruta sea correcta
import '../../styles/Header.css';

const Header = () => {
    const [userName, setUserName] = useState(authStore.getUserName());

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
        authStore.logout(); // Cerramos la sesión
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
                        <span className="user-name">
                            {userName}
                        </span>
                        <button onClick={handleLogout}>Cerrar Sesión</button>
                    </div>
                )}
            </nav>
            <button className="menu-toggle" onClick={() => { /* Lógica para menú móvil */ }}>
                ☰
            </button>
        </header>
    );
};

export default Header;

