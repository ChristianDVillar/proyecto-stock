// src/components/Footer.jsx
import React from 'react';

const Footer = () => {
    return (
        <footer style={{
            background: '#6c5ce7',
            color: '#ffffff',
            textAlign: 'center',
            padding: '24px',
            marginTop: 'auto'
        }}>
            <p style={{
                margin: 0,
                opacity: 0.8,
                fontSize: '14px'
            }}>
                &copy; 2024 Control de Stock. Todos los derechos reservados.
            </p>
        </footer>
    );
};

export default Footer;