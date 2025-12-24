import React, { useState, useEffect } from 'react';

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
            const token = localStorage.getItem('jwt_token');

            if (!token) {
                handleLogout();
                return;
            }

            const response = await fetch('http://localhost:5000/api/stock/types', {
                headers: {
                    'Authorization': `Bearer ${token}`,
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
            const token = localStorage.getItem('jwt_token');
            if (!token) {
                handleLogout();
                return;
            }

            const response = await fetch('http://localhost:5000/api/stock/types', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ name: customType })
            });

            if (response.status === 401) {
                handleLogout();
                return;
            }

            const textResponse = await response.text();
            console.log('Respuesta del servidor (agregar tipo):', textResponse);

            if (!response.ok) {
                throw new Error(`Error al agregar tipo: ${textResponse}`);
            }

            const result = JSON.parse(textResponse);
            console.log('Tipo personalizado agregado:', result);
            
            await fetchStockTypes();
            
            const newTypeId = `custom_${result.type.id}`;
            onChange(newTypeId);
            setShowCustomInput(false);
            setCustomType('');
        } catch (error) {
            console.error('Error detallado:', error);
            if (error.message.includes('Token inválido') || error.message.includes('Authorization')) {
                handleLogout();
            } else {
                alert('Error al agregar el tipo personalizado: ' + error.message);
            }
        }
    };

    if (loading) {
        return <div>Cargando tipos...</div>;
    }

    if (error) {
        return (
            <div>
                <div style={{color: 'red', marginBottom: '10px'}}>Error: {error}</div>
                <button 
                    className="btn btn-primary" 
                    onClick={fetchStockTypes}
                >
                    Reintentar
                </button>
                <button 
                    className="btn btn-secondary ml-2" 
                    onClick={handleLogout}
                >
                    Cerrar Sesión
                </button>
            </div>
        );
    }

    return (
        <div className="device-type-selector">
            <select 
                value={value} 
                onChange={handleTypeChange}
                className="form-control"
                id="dispositivo"
            >
                <option value="">Seleccione un tipo</option>
                {types.map(type => (
                    <option key={type.id} value={type.id}>
                        {type.name}
                    </option>
                ))}
            </select>

            {showCustomInput && (
                <div className="custom-type-input mt-2">
                    <div className="input-group">
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Ingrese nuevo tipo"
                            value={customType}
                            onChange={handleCustomTypeChange}
                        />
                        <div className="input-group-append">
                            <button 
                                className="btn btn-primary" 
                                onClick={handleCustomTypeSubmit}
                            >
                                Agregar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DeviceTypeSelector; 