import React, { useState } from 'react';
import '../../styles/Header.css';

const Header = () => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    };

    return (
        <header className="header">
            <div className="logo">
                Control de Stock
            </div>
            <nav className={`nav ${isOpen ? 'open' : ''}`}>
                <a href="#nuevo-inventario">Nuevo Inventario</a>
                <a href="#consultar">Consultar Inventario</a>
                <a href="mailto:christianvillar@live.com.ar" id="contact-link">Contacto</a>
            </nav>
            <button className="menu-toggle" onClick={toggleMenu}>
                ☰
            </button>
        </header>
    );
};

export default Header;
