import React, { useState, useEffect, useRef } from 'react';
import { BrowserMultiFormatReader, BrowserCodeReader } from '@zxing/browser';
import * as ZXing from '@zxing/library';
import { FaTrash, FaPencilAlt, FaCamera, FaBarcode, FaStop } from 'react-icons/fa';
import DeviceTypeSelector from './DeviceTypeSelector';
import { useNavigate } from 'react-router-dom';
import authStore from '../services/AuthStore';

const NewInventory = () => {
    const navigate = useNavigate();
    const [scannedBarcode, setScannedBarcode] = useState('');
    const [imageSrc, setImageSrc] = useState('');
    const [isScanning, setIsScanning] = useState(false);
    const [selectedCamera, setSelectedCamera] = useState('');
    const [availableCameras, setAvailableCameras] = useState([]);
    const videoRef = useRef(null);
    const codeReaderRef = useRef(null);
    const [formData, setFormData] = useState({
        inventario: '',
        dispositivo: '',
        modelo: '',
        descripcion: '',
        cantidad: ''
    });
    const [rows, setRows] = useState([]);
    const [isEditing, setIsEditing] = useState(false);
    const [editRowId, setEditRowId] = useState(null);

    useEffect(() => {
        if (!authStore.isLoggedIn()) {
            console.log('Usuario no autenticado, redirigiendo al login');
            navigate('/login');
        }
    }, [navigate]);

    useEffect(() => {
        const initializeReader = async () => {
            try {
                // Configurar el lector con opciones optimizadas
                const hints = new Map();
                const formats = [
                    ZXing.BarcodeFormat.CODE_39,
                    ZXing.BarcodeFormat.CODE_128,
                    ZXing.BarcodeFormat.EAN_13,
                    ZXing.BarcodeFormat.EAN_8,
                    ZXing.BarcodeFormat.UPC_A,
                    ZXing.BarcodeFormat.UPC_E
                ];

                const reader = new BrowserMultiFormatReader();
                reader.hints.set(ZXing.DecodeHintType.POSSIBLE_FORMATS, formats);
                reader.hints.set(ZXing.DecodeHintType.TRY_HARDER, true);
                
                codeReaderRef.current = reader;

                // Obtener lista de cámaras disponibles
                const devices = await BrowserCodeReader.listVideoInputDevices();
                console.log('Cámaras disponibles:', devices);
                setAvailableCameras(devices);

                // Seleccionar la Logitech C270 si está disponible
                const logitechCamera = devices.find(device => 
                    device.label.toLowerCase().includes('logitech') && 
                    device.label.toLowerCase().includes('c270')
                );
                
                if (logitechCamera) {
                    setSelectedCamera(logitechCamera.deviceId);
                } else if (devices.length > 0) {
                    setSelectedCamera(devices[0].deviceId);
                }
            } catch (error) {
                console.error('Error initializing camera:', error);
            }
        };

        initializeReader();

        return () => {
            if (isScanning) {
                stopScanning();
            }
            if (codeReaderRef.current) {
                BrowserCodeReader.releaseAllStreams();
                if (videoRef.current) {
                    BrowserCodeReader.cleanVideoSource(videoRef.current);
                }
            }
        };
    }, []);

    const startScanning = async () => {
        try {
            setIsScanning(true);
            
            await new Promise(resolve => setTimeout(resolve, 100));

            if (!videoRef.current) {
                console.error('Video element not found');
                setIsScanning(false);
                return;
            }

            // Configuración optimizada para la Logitech C270
            const constraints = {
                video: {
                    deviceId: selectedCamera ? { exact: selectedCamera } : undefined,
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "environment",
                    focusMode: { ideal: "continuous" },
                    exposureMode: { ideal: "continuous" },
                    whiteBalanceMode: { ideal: "continuous" },
                    frameRate: { ideal: 30 },
                    brightness: { ideal: 100 },
                    contrast: { ideal: 100 },
                    saturation: { ideal: 100 },
                    sharpness: { ideal: 100 },
                    zoom: { ideal: 100 }
                }
            };

            await codeReaderRef.current.decodeFromConstraints(constraints, videoRef.current, (result, error) => {
                if (result) {
                    console.log('Código detectado:', result);
                    setScannedBarcode(result.getText());
                }
                if (error) {
                    // Solo logear errores que no sean de "no QR code found"
                    if (!error.message.includes('no QR code found')) {
                        console.log('Error scanning:', error);
                    }
                }
            });

        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Error al acceder a la cámara: ' + error.message);
            setIsScanning(false);
        }
    };

    const stopScanning = async () => {
        try {
            BrowserCodeReader.releaseAllStreams();
            if (videoRef.current) {
                BrowserCodeReader.cleanVideoSource(videoRef.current);
            }
        } catch (err) {
            console.error("Error stopping scanner:", err);
        } finally {
            setIsScanning(false);
        }
    };

    const handleImageChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            setImageSrc(event.target.result);

            try {
                const img = new Image();
                img.src = event.target.result;
                await new Promise((resolve) => {
                    img.onload = resolve;
                });

                const result = await codeReaderRef.current.decodeFromImage(img);
                if (result) {
                    setScannedBarcode(result.getText());
                }
            } catch (error) {
                console.error('Error al procesar la imagen:', error);
                setScannedBarcode('');
                alert("No se detectó ningún código de barras. Por favor, intente de nuevo con una imagen más clara.");
            }
        };

        reader.onerror = () => {
            setScannedBarcode('');
            alert("Error al leer el archivo. Por favor, intente de nuevo.");
        };

        reader.readAsDataURL(file);
    };

    const handleInputChange = (e) => {
        const { id, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [id]: value
        }));
    };

    const handleDeviceTypeChange = (value) => {
        setFormData(prevState => ({
            ...prevState,
            dispositivo: value
        }));
    };

    const handleSave = () => {
        const currentTime = new Date();
        const newRow = {
            id: isEditing ? editRowId : currentTime.getTime(),
            barcode: scannedBarcode || "S/N",
            inventario: formData.inventario || "S/N",
            dispositivo: formData.dispositivo || "S/N",
            modelo: formData.modelo || "S/N",
            descripcion: formData.descripcion || "S/N",
            cantidad: formData.cantidad || "S/N",
            dateAdded: `${currentTime.toLocaleDateString()} ${currentTime.toLocaleTimeString()}`
        };

        if (isEditing) {
            setRows(prevRows => prevRows.map(row => row.id === editRowId ? newRow : row));
            setIsEditing(false);
            setEditRowId(null);
        } else {
            setRows(prevRows => [...prevRows, newRow]);
        }

        setScannedBarcode('');
        setFormData({
            inventario: '',
            dispositivo: '',
            modelo: '',
            descripcion: '',
            cantidad: ''
        });
        setImageSrc('');
    };

    const handleDelete = (id) => {
        setRows(prevRows => prevRows.filter(row => row.id !== id));
    };

    const handleEdit = (id) => {
        const row = rows.find(row => row.id === id);
        setScannedBarcode(row.barcode);
        setFormData({
            inventario: row.inventario === "S/N" ? '' : row.inventario,
            dispositivo: row.dispositivo === "S/N" ? '' : row.dispositivo,
            modelo: row.modelo === "S/N" ? '' : row.modelo,
            descripcion: row.descripcion === "S/N" ? '' : row.descripcion,
            cantidad: row.cantidad === "S/N" ? '' : row.cantidad
        });
        setIsEditing(true);
        setEditRowId(id);
    };

    const handleSaveToServer = async () => {
        try {
            // Verificar autenticación primero
            if (!authStore.isLoggedIn()) {
                console.log('Usuario no autenticado, redirigiendo al login');
                navigate('/login');
                return;
            }

            const token = authStore.getToken();
            if (!token) {
                console.log('No se encontró token, redirigiendo al login');
                navigate('/login');
                return;
            }

            if (!scannedBarcode || !formData.inventario || !formData.dispositivo || !formData.modelo) {
                throw new Error('Por favor, complete todos los campos requeridos.');
            }

            const cantidad = parseInt(formData.cantidad);
            if (isNaN(cantidad) || cantidad <= 0) {
                throw new Error('La cantidad debe ser un número mayor que 0.');
            }

            const requestData = {
                barcode: scannedBarcode,
                inventario: formData.inventario,
                dispositivo: formData.dispositivo,
                modelo: formData.modelo,
                descripcion: formData.descripcion || '',
                cantidad: cantidad,
                purchase_date: new Date().toISOString().split('T')[0],
                location: 'default'
            };

            console.log('Enviando datos al servidor:', requestData);

            const response = await fetch('http://localhost:5000/api/stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token,
                    'Accept': 'application/json'
                },
                credentials: 'include',
                mode: 'cors',
                body: JSON.stringify(requestData)
            });

            if (response.status === 401) {
                console.log('Token expirado o inválido');
                await authStore.clearState(true);
                navigate('/login');
                return;
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Error al guardar en el servidor');
            }

            const data = await response.json();
            console.log('Respuesta del servidor:', data);

            // Limpiar el formulario después de guardar exitosamente
            setScannedBarcode('');
            setFormData({
                inventario: '',
                dispositivo: '',
                modelo: '',
                descripcion: '',
                cantidad: ''
            });
            setRows([]);
            alert('Datos guardados exitosamente');

        } catch (error) {
            console.error('Error al guardar:', error);
            alert(error.message || 'Error al guardar en el servidor');
        }
    };

    const handleCameraChange = (event) => {
        const newCameraId = event.target.value;
        setSelectedCamera(newCameraId);
        if (isScanning) {
            stopScanning().then(() => startScanning());
        }
    };

    return (
        <div className="container" style={{ 
            maxWidth: '1200px', 
            margin: '0 auto', 
            padding: '20px',
            backgroundColor: '#f8f9fa',
            minHeight: '100vh'
        }}>
            <div className="card mb-4" style={{
                backgroundColor: '#ffffff',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e9ecef'
            }}>
                <div className="card-header" style={{
                    backgroundColor: '#6c5ce7',
                    color: '#ffffff',
                    padding: '20px',
                    borderRadius: '12px 12px 0 0',
                    borderBottom: 'none'
                }}>
                    <h2 className="card-title" style={{ margin: 0, fontSize: '24px', fontWeight: '600' }}>
                        Nuevo Inventario
                    </h2>
                </div>
                
                <div className="form-group mb-4" style={{ padding: '20px' }}>
                    <div className="scanner-controls" style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '10px',
                        marginBottom: '20px'
                    }}>
                        {availableCameras.length > 1 && (
                            <select
                                value={selectedCamera}
                                onChange={handleCameraChange}
                                className="camera-select mr-2"
                                style={{
                                    padding: '10px 15px',
                                    border: '2px solid #74b9ff',
                                    borderRadius: '8px',
                                    backgroundColor: '#ffffff',
                                    color: '#2d3436',
                                    fontSize: '14px',
                                    outline: 'none'
                                }}
                            >
                                {availableCameras.map(camera => (
                                    <option key={camera.deviceId} value={camera.deviceId}>
                                        {camera.label || `Cámara ${camera.deviceId}`}
                                    </option>
                                ))}
                            </select>
                        )}
                        {!isScanning ? (
                            <button 
                                className="btn btn-primary mr-2" 
                                onClick={startScanning}
                                style={{
                                    backgroundColor: '#00b894',
                                    color: '#ffffff',
                                    border: 'none',
                                    padding: '12px 20px',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    fontWeight: '500',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    transition: 'background-color 0.3s ease'
                                }}
                                onMouseOver={(e) => e.target.style.backgroundColor = '#00a085'}
                                onMouseOut={(e) => e.target.style.backgroundColor = '#00b894'}
                            >
                                <FaBarcode /> Iniciar Escaneo
                            </button>
                        ) : (
                            <button 
                                className="btn btn-error mr-2" 
                                onClick={stopScanning}
                                style={{
                                    backgroundColor: '#e17055',
                                    color: '#ffffff',
                                    border: 'none',
                                    padding: '12px 20px',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    fontWeight: '500',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    transition: 'background-color 0.3s ease'
                                }}
                                onMouseOver={(e) => e.target.style.backgroundColor = '#d63031'}
                                onMouseOut={(e) => e.target.style.backgroundColor = '#e17055'}
                            >
                                <FaStop /> Detener Escaneo
                            </button>
                        )}
                        <label className="btn btn-ghost" style={{
                            backgroundColor: '#fdcb6e',
                            color: '#2d3436',
                            border: 'none',
                            padding: '12px 20px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: '500',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            transition: 'background-color 0.3s ease'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#f39c12'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#fdcb6e'}
                        >
                            <FaCamera />
                            Cargar Imagen
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                className="hidden"
                            />
                        </label>
                    </div>
                    
                    <div className="video-container mb-4" style={{ 
                        display: isScanning ? 'block' : 'none',
                        backgroundColor: '#2d3436',
                        borderRadius: '8px',
                        overflow: 'hidden'
                    }}>
                        <video 
                            ref={videoRef} 
                            className="scanner-video"
                            style={{ 
                                width: '100%',
                                maxWidth: '1280px',
                                height: 'auto',
                                margin: '0 auto',
                                backgroundColor: '#2d3436'
                            }}
                            autoPlay
                            playsInline
                        />
                    </div>
                    
                    {imageSrc && (
                        <div className="preview-container mb-4" style={{
                            backgroundColor: '#ffffff',
                            padding: '15px',
                            borderRadius: '8px',
                            border: '2px solid #74b9ff'
                        }}>
                            <h4 style={{ marginBottom: '10px', color: '#2d3436' }}>Vista Previa:</h4>
                            <img src={imageSrc} alt="Preview" className="preview-image" style={{
                                maxWidth: '100%',
                                height: 'auto',
                                borderRadius: '4px'
                            }} />
                        </div>
                    )}
                    
                    {scannedBarcode && (
                        <div className="alert alert-success" style={{
                            backgroundColor: '#00b894',
                            color: '#ffffff',
                            padding: '15px',
                            borderRadius: '8px',
                            border: '2px solid #00a085',
                            marginBottom: '20px'
                        }}>
                            <strong>Código escaneado:</strong> {scannedBarcode}
                        </div>
                    )}
                </div>

                <form className="inventory-form" style={{ padding: '0 20px 20px' }}>
                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label className="form-label" htmlFor="inventario" style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Número de Inventario:
                        </label>
                        <input
                            type="text"
                            id="inventario"
                            className="form-input"
                            value={formData.inventario}
                            onChange={handleInputChange}
                            style={{
                                width: '100%',
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
                    </div>
                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label className="form-label" htmlFor="codigo-escaneado" style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Código Escaneado:
                        </label>
                        <input
                            type="text"
                            id="codigo-escaneado"
                            className="form-input"
                            value={scannedBarcode}
                            readOnly
                            style={{
                                width: '100%',
                                padding: '12px',
                                border: '2px solid #dfe6e9',
                                borderRadius: '8px',
                                fontSize: '14px',
                                backgroundColor: '#f8f9fa',
                                color: '#636e72'
                            }}
                        />
                    </div>
                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label className="form-label" htmlFor="dispositivo" style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Dispositivo:
                        </label>
                        <DeviceTypeSelector
                            value={formData.dispositivo}
                            onChange={handleDeviceTypeChange}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label className="form-label" htmlFor="modelo" style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Modelo:
                        </label>
                        <input
                            type="text"
                            id="modelo"
                            className="form-input"
                            value={formData.modelo}
                            onChange={handleInputChange}
                            style={{
                                width: '100%',
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
                    </div>

                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label className="form-label" htmlFor="descripcion" style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Descripción:
                        </label>
                        <textarea
                            id="descripcion"
                            className="form-input"
                            value={formData.descripcion}
                            onChange={handleInputChange}
                            style={{
                                width: '100%',
                                padding: '12px',
                                border: '2px solid #dfe6e9',
                                borderRadius: '8px',
                                fontSize: '14px',
                                outline: 'none',
                                transition: 'border-color 0.3s ease',
                                resize: 'vertical',
                                minHeight: '80px'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                            onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '20px' }}>
                        <label className="form-label" htmlFor="cantidad" style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Cantidad:
                        </label>
                        <input
                            type="number"
                            id="cantidad"
                            className="form-input"
                            value={formData.cantidad}
                            onChange={handleInputChange}
                            min="1"
                            style={{
                                width: '100%',
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
                    </div>

                    <div className="form-actions" style={{
                        display: 'flex',
                        gap: '15px',
                        marginTop: '30px'
                    }}>
                        <button
                            type="button"
                            className="btn btn-primary mr-2"
                            onClick={handleSave}
                            style={{
                                backgroundColor: '#00b894',
                                color: '#ffffff',
                                border: 'none',
                                padding: '12px 24px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '500',
                                transition: 'background-color 0.3s ease'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = '#00a085'}
                            onMouseOut={(e) => e.target.style.backgroundColor = '#00b894'}
                        >
                            {isEditing ? 'Actualizar' : 'Agregar'}
                        </button>
                        <button
                            type="button"
                            className="btn btn-success"
                            onClick={handleSaveToServer}
                            style={{
                                backgroundColor: '#6c5ce7',
                                color: '#ffffff',
                                border: 'none',
                                padding: '12px 24px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '14px',
                                fontWeight: '500',
                                transition: 'background-color 0.3s ease'
                            }}
                            onMouseOver={(e) => e.target.style.backgroundColor = '#5f3dc4'}
                            onMouseOut={(e) => e.target.style.backgroundColor = '#6c5ce7'}
                        >
                            Guardar en Servidor
                        </button>
                    </div>
                </form>
            </div>

            <div className="card" style={{
                backgroundColor: '#ffffff',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e9ecef'
            }}>
                <div className="card-header" style={{
                    backgroundColor: '#a29bfe',
                    color: '#ffffff',
                    padding: '20px',
                    borderRadius: '12px 12px 0 0',
                    borderBottom: 'none'
                }}>
                    <h3 className="card-title" style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
                        Items Escaneados
                    </h3>
                </div>
                <div className="table-responsive" style={{ overflowX: 'auto' }}>
                    <table className="table" style={{
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
                                }}>Código</th>
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
                                }}>Descripción</th>
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
                                }}>Fecha</th>
                                <th style={{
                                    padding: '15px',
                                    textAlign: 'left',
                                    borderBottom: '2px solid #e9ecef',
                                    color: '#2d3436',
                                    fontWeight: '600',
                                    fontSize: '14px'
                                }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map(row => (
                                <tr key={row.id} style={{
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
                                    }}>{row.barcode}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{row.inventario}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{row.dispositivo}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{row.modelo}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{row.descripcion}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#2d3436',
                                        fontSize: '14px'
                                    }}>{row.cantidad}</td>
                                    <td style={{
                                        padding: '15px',
                                        color: '#636e72',
                                        fontSize: '14px'
                                    }}>{row.dateAdded}</td>
                                    <td style={{ padding: '15px' }}>
                                        <button
                                            className="btn btn-icon btn-ghost mr-2"
                                            onClick={() => handleEdit(row.id)}
                                            style={{
                                                backgroundColor: '#74b9ff',
                                                color: '#ffffff',
                                                border: 'none',
                                                padding: '8px',
                                                borderRadius: '6px',
                                                cursor: 'pointer',
                                                marginRight: '8px',
                                                transition: 'background-color 0.3s ease'
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = '#0984e3'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = '#74b9ff'}
                                        >
                                            <FaPencilAlt />
                                        </button>
                                        <button
                                            className="btn btn-icon btn-ghost-error"
                                            onClick={() => handleDelete(row.id)}
                                            style={{
                                                backgroundColor: '#fd79a8',
                                                color: '#ffffff',
                                                border: 'none',
                                                padding: '8px',
                                                borderRadius: '6px',
                                                cursor: 'pointer',
                                                transition: 'background-color 0.3s ease'
                                            }}
                                            onMouseOver={(e) => e.target.style.backgroundColor = '#e84393'}
                                            onMouseOut={(e) => e.target.style.backgroundColor = '#fd79a8'}
                                        >
                                            <FaTrash />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default NewInventory;
