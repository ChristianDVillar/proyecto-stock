import React, { useState, useEffect } from 'react';
import authStore from '../services/AuthStore';

const DeviceTypeSelector = ({ value, onChange }) => {
    const [types, setTypes] = useState([]);
    const [showCustomInput, setShowCustomInput] = useState(false);
    const [customType, setCustomType] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const handleLogout = () => {
        localStorage.removeItem('jwt_token');
        window.location.href = '/login';
    };

    const fetchStockTypes = async () => {
        try {
            setLoading(true);
            setError(null);
            const token = authStore.getToken();

            if (!token) {
                handleLogout();
                return;
            }

            const response = await fetch('http://localhost:5000/api/stock/types', {
                headers: {
                    'Authorization': token,
                    'Accept': 'application/json'
                }
            });

            if (response.status === 401) {
                handleLogout();
                return;
            }

            const textResponse = await response.text();
            console.log('Respuesta del servidor:', textResponse);

            if (!response.ok) {
                throw new Error(`Error del servidor: ${textResponse}`);
            }

            const data = JSON.parse(textResponse);
            console.log('Tipos recibidos:', data);

            if (!data.types || !Array.isArray(data.types)) {
                throw new Error('Formato de respuesta inválido');
            }

            setTypes(data.types);
        } catch (error) {
            console.error('Error detallado:', error);
            if (error.message.includes('Token inválido') || error.message.includes('Authorization')) {
                handleLogout();
            } else {
                setError(error.message);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStockTypes();
    }, []);

    const handleTypeChange = (e) => {
        const selectedValue = e.target.value;
        console.log('Tipo seleccionado:', selectedValue);
        if (selectedValue === 'otro') {
            setShowCustomInput(true);
            onChange(selectedValue);
        } else {
            setShowCustomInput(false);
            onChange(selectedValue);
        }
    };

    const handleCustomTypeChange = (e) => {
        const newCustomType = e.target.value;
        setCustomType(newCustomType);
    };

    const handleCustomTypeSubmit = async () => {
        if (!customType.trim()) return;

        try {
            const token = authStore.getToken();
            if (!token) {
                handleLogout();
                return;
            }

            const response = await fetch('http://localhost:5000/api/stock/types', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token,
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ type: customType.trim() })
            });

            if (response.status === 401) {
                handleLogout();
                return;
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al agregar el tipo');
            }

            // Recargar los tipos después de agregar uno nuevo
            await fetchStockTypes();
            setShowCustomInput(false);
            setCustomType('');
            onChange(customType.trim());
        } catch (error) {
            console.error('Error al agregar tipo:', error);
            setError(error.message);
        }
    };

    if (loading) {
        return (
            <div style={{
                padding: '12px',
                border: '2px solid #dfe6e9',
                borderRadius: '8px',
                backgroundColor: '#f8f9fa',
                color: '#636e72',
                fontSize: '14px'
            }}>
                Cargando tipos de dispositivos...
            </div>
        );
    }

    if (error) {
        return (
            <div style={{
                padding: '12px',
                border: '2px solid #e17055',
                borderRadius: '8px',
                backgroundColor: 'rgba(225, 112, 85, 0.1)',
                color: '#e17055',
                fontSize: '14px'
            }}>
                Error: {error}
            </div>
        );
    }

    return (
        <div style={{ marginBottom: '20px' }}>
            <select
                value={value}
                onChange={handleTypeChange}
                style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #dfe6e9',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'border-color 0.3s ease',
                    backgroundColor: '#ffffff',
                    color: '#2d3436'
                }}
                onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
            >
                <option value="">Selecciona un tipo de dispositivo</option>
                {types.map((type) => (
                    <option key={type.id} value={type.name}>
                        {type.name}
                    </option>
                ))}
                <option value="otro">Otro (especificar)</option>
            </select>

            {showCustomInput && (
                <div style={{ marginTop: '12px' }}>
                    <div style={{
                        display: 'flex',
                        gap: '8px',
                        alignItems: 'center'
                    }}>
                        <input
                            type="text"
                            value={customType}
                            onChange={handleCustomTypeChange}
                            placeholder="Especifica el tipo de dispositivo"
                            style={{
                                flex: 1,
                                padding: '12px',
                                border: '2px solid #dfe6e9',
                                borderRadius: '8px',
                                fontSize: '14px',
                                outline: 'none',
                                transition: 'border-color 0.3s ease'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                            onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                        />
                        <button
                            onClick={handleCustomTypeSubmit}
                            style={{
                                background: '#fdcb6e',
                                color: '#2d3436',
                                border: 'none',
                                padding: '12px 16px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '500',
                                transition: 'background-color 0.3s ease'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = '#f39c12'}
                            onMouseOut={(e) => e.target.style.backgroundColor = '#fdcb6e'}
                        >
                            Agregar
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DeviceTypeSelector; 