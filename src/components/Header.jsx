import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authStore from '../services/AuthStore';

const Header = ({ isLoggedIn, isAdmin }) => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        await authStore.clearState(true);
        navigate('/login');
    };

    if (!isLoggedIn) return null;

    return (
        <header style={{
            background: '#6c5ce7',
            color: '#ffffff',
            padding: '16px 24px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            position: 'sticky',
            top: 0,
            zIndex: 1000
        }}>
            <nav style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                maxWidth: '1200px',
                margin: '0 auto'
            }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '24px'
                }}>
                    <Link 
                        to="/nuevo-inventario" 
                        style={{
                            color: '#ffffff',
                            textDecoration: 'none',
                            padding: '8px 16px',
                            borderRadius: '6px',
                            transition: 'background-color 0.3s ease',
                            fontWeight: '500'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
                        onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
                    >
                        Nuevo Inventario
                    </Link>
                    <Link 
                        to="/consultar-inventario" 
                        style={{
                            color: '#ffffff',
                            textDecoration: 'none',
                            padding: '8px 16px',
                            borderRadius: '6px',
                            transition: 'background-color 0.3s ease',
                            fontWeight: '500'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
                        onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
                    >
                        Consultar Inventario
                    </Link>
                    {isAdmin && (
                        <Link 
                            to="/admin" 
                            style={{
                                color: '#ffffff',
                                textDecoration: 'none',
                                padding: '8px 16px',
                                borderRadius: '6px',
                                transition: 'background-color 0.3s ease',
                                fontWeight: '500'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
                            onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
                        >
                            Administración
                        </Link>
                    )}
                </div>
                
                <button 
                    onClick={handleLogout} 
                    style={{
                        background: '#e17055',
                        color: '#ffffff',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        transition: 'background-color 0.3s ease'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = '#d63031'}
                    onMouseOut={(e) => e.target.style.backgroundColor = '#e17055'}
                >
                    Cerrar Sesión
                </button>
            </nav>
        </header>
    );
};

export default Header;
