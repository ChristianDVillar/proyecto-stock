import React, { useState, useEffect } from 'react';
import '../../styles/Header.css';

const Header = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    };

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const formattedTime = currentTime.toLocaleTimeString();
    const formattedDate = currentTime.toLocaleDateString();

    return (
        <header className="header">
            <div className="logo">
                Control de Stock
            </div>
            <nav className={`nav ${isOpen ? 'open' : ''}`}>
                <a href="#nuevo-inventario">Nuevo Inventario</a>
                <a href="#consultar">Consultar Inventario</a>
                <a href="mailto:christianvillar@live.com.ar" id="contact-link">Contacto</a>
                <div className="date-time">
                    {formattedDate} {formattedTime}
                </div>
            </nav>
            <button className="menu-toggle" onClick={toggleMenu}>
                ☰
            </button>
        </header>
    );
};

export default Header;

