// src/components/Contact.js
import React, { useState } from 'react';
import '../../styles/Contact.css'; // Add CSS styles for the modal here

const Contact = () => {
    const [isOpen, setIsOpen] = useState(false);

    const openModal = () => setIsOpen(true);
    const closeModal = () => setIsOpen(false);

    return (
        <>
            <button onClick={openModal} id="contact-link">Contacto</button>
            {isOpen && (
                <div id="contact-modal" className="modal">
                    <div className="modal-content">
                        <span className="close-button" onClick={closeModal}>&times;</span>
                        <h1>Contacto</h1>
                        <p>Para más información, contacta con nosotros en <a href="mailto:christianvillar@live.com.ar">christianvillar@live.com.ar</a></p>
                    </div>
                </div>
            )}
        </>
    );
};

export default Contact;
