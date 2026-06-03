import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import authStore from '../../stores/AuthStore';
import '../../styles/Header.css';

const Header = ({ isAdmin }) => {
    const [userName, setUserName] = useState(authStore.getUserName());
    const [showDropdown, setShowDropdown] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());
    const navigate = useNavigate();

    useEffect(() => {
        const handleAuthChange = () => setUserName(authStore.getUserName());
        authStore.on('change', handleAuthChange);
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => {
            authStore.removeListener('change', handleAuthChange);
            clearInterval(timer);
        };
    }, []);

    const handleLogout = () => {
        authStore.logout();
        setShowDropdown(false);
    };

    const handleNav = (path) => {
        setShowDropdown(false);
        navigate(path);
    };

    return (
        <header className="header">
            <div className="logo">Control de Stock</div>
            <nav className="nav">
                {isAdmin && (
                    <>
                        <NavLink to="/dashboard" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Dashboard
                        </NavLink>
                        <NavLink to="/" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Nuevo Inventario
                        </NavLink>
                        <NavLink to="/consultar" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Consultar Inventario
                        </NavLink>
                        <NavLink to="/proveedores" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Proveedores
                        </NavLink>
                        <NavLink to="/ordenes-compra" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Órdenes de compra
                        </NavLink>
                        <NavLink to="/almacenes" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Almacenes
                        </NavLink>
                        <NavLink to="/transferencias" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                            Transferencias
                        </NavLink>
                    </>
                )}
                <NavLink to="/solicitar" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                    Solicitar elementos
                </NavLink>
                {isAdmin && (
                    <NavLink to="/admin" className={({ isActive }) => 'nav-button' + (isActive ? ' active' : '')}>
                        Gestión de Usuarios
                    </NavLink>
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
                                <button className="admin-option" onClick={() => handleNav('/admin')}>
                                    Gestión de Usuarios
                                </button>
                            )}
                            <button onClick={handleLogout}>Cerrar Sesión</button>
                        </div>
                    )}
                </div>
            </nav>
        </header>
    );
};

export default Header;
