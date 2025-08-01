import React, { useState, useEffect } from 'react';
import authStore from '../services/AuthStore';

const ConsultInventory = () => {
    const [inventory, setInventory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchInventory();
    }, []);

    const fetchInventory = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await fetch('http://localhost:5000/api/stock/inventory', {
                method: 'GET',
                headers: {
                    'Authorization': authStore.getToken(),
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error al cargar el inventario');
            }

            const data = await response.json();
            setInventory(data.detalle || []);
        } catch (err) {
            console.error('Error fetching inventory:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '200px',
                color: '#2d3436',
                fontSize: '18px'
            }}>
                Cargando inventario...
            </div>
        );
    }

    if (error) {
        return (
            <div style={{
                backgroundColor: 'rgba(225, 112, 85, 0.1)',
                border: '1px solid #e17055',
                color: '#e17055',
                padding: '16px',
                borderRadius: '8px',
                margin: '20px',
                textAlign: 'center'
            }}>
                Error: {error}
            </div>
        );
    }

    return (
        <div style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '20px'
        }}>
            <div style={{
                backgroundColor: '#ffffff',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e9ecef',
                overflow: 'hidden'
            }}>
                <div style={{
                    background: '#a29bfe',
                    color: '#ffffff',
                    padding: '20px',
                    borderBottom: '1px solid #e9ecef'
                }}>
                    <h2 style={{
                        margin: 0,
                        fontSize: '20px',
                        fontWeight: '600'
                    }}>
                        Consultar Inventario
                    </h2>
                </div>
                
                <div style={{ overflowX: 'auto' }}>
                    <table style={{
                        width: '100%',
                        borderCollapse: 'collapse',
                        backgroundColor: '#ffffff'
                    }}>
                        <thead style={{ backgroundColor: '#f8f9fa' }}>
                            <tr>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Código de Barras</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Inventario</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Dispositivo</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Modelo</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Cantidad</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Estado</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Ubicación</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inventory.length === 0 ? (
                                <tr>
                                    <td colSpan="7" style={{
                                        padding: '40px',
                                        textAlign: 'center',
                                        color: '#636e72',
                                        fontSize: '16px'
                                    }}>
                                        No hay items en el inventario
                                    </td>
                                </tr>
                            ) : (
                                inventory.map((item) => (
                                    <tr key={item.id} style={{
                                        borderBottom: '1px solid #f1f2f6',
                                        transition: 'background-color 0.3s ease'
                                    }}
                                    onMouseOver={(e) => e.target.parentElement.style.backgroundColor = '#f8f9fa'}
                                    onMouseOut={(e) => e.target.parentElement.style.backgroundColor = '#ffffff'}
                                    >
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px',
                                            fontFamily: 'monospace'
                                        }}>{item.barcode}</td>
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px'
                                        }}>{item.inventario}</td>
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px'
                                        }}>{item.dispositivo}</td>
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px'
                                        }}>{item.modelo}</td>
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px'
                                        }}>{item.cantidad}</td>
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px'
                                        }}>{item.status}</td>
                                        <td style={{
                                            padding: '15px',
                                            color: '#2d3436',
                                            fontSize: '14px'
                                        }}>{item.location}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default ConsultInventory;
