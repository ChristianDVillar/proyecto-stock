// src/components/Contact.js
import React, { useState } from 'react';

const Contact = () => {
    const [isOpen, setIsOpen] = useState(false);

    const openModal = () => setIsOpen(true);
    const closeModal = () => setIsOpen(false);

    return (
        <>
            <button onClick={openModal} className="btn btn-ghost" id="contact-link">Contacto</button>
            {isOpen && (
                <div className="modal-overlay" id="contact-modal">
                    <div className="modal-content card">
                        <div className="card-header">
                            <button className="btn btn-icon btn-ghost" onClick={closeModal}>&times;</button>
                            <h2 className="card-title">Contacto</h2>
                        </div>
                        <p className="mb-4">
                            Para más información, contacta con nosotros en{' '}
                            <a href="mailto:christianvillar@live.com.ar" className="text-accent">
                                christianvillar@live.com.ar
                            </a>
                        </p>
                    </div>
                </div>
            )}
        </>
    );
};

export default Contact;
