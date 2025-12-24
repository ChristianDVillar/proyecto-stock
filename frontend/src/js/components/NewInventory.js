import React, { useState, useEffect, useRef } from 'react';
import Quagga from '@ericblade/quagga2';
import { FaTrash, FaPencilAlt, FaCamera, FaBarcode, FaStop } from 'react-icons/fa';
import '../../styles/NewInventory.css';
import DeviceTypeSelector from './DeviceTypeSelector';
import authStore from '../../stores/AuthStore';

const NewInventory = () => {
    const [scannedBarcode, setScannedBarcode] = useState('');
    const [imageSrc, setImageSrc] = useState('');
    const [isScanning, setIsScanning] = useState(false);
    const videoRef = useRef(null);
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
        return () => {
            if (isScanning) {
                stopScanning();
            }
        };
    }, [isScanning]);

    const startScanning = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: "environment",
                    width: { min: 640, ideal: 1280, max: 1920 },
                    height: { min: 480, ideal: 720, max: 1080 }
                }
            });

            if (!videoRef.current) {
                console.error('Video element not found');
                return;
            }

            videoRef.current.srcObject = stream;
            await new Promise((resolve) => {
                videoRef.current.onloadedmetadata = () => {
                    resolve();
                };
            });

            const config = {
                inputStream: {
                    type: "LiveStream",
                    constraints: {
                        ...stream.getVideoTracks()[0].getSettings()
                    },
                    area: {
                        top: "0%",
                        right: "0%",
                        left: "0%",
                        bottom: "0%"
                    },
                    target: videoRef.current
                },
                decoder: {
                    readers: [
                        "ean_reader",
                        "ean_8_reader",
                        "code_128_reader",
                        "code_39_reader",
                        "upc_reader",
                        "upc_e_reader"
                    ]
                },
                locate: true
            };

            try {
                await Quagga.init(config);
                Quagga.start();
                setIsScanning(true);

                Quagga.onDetected((result) => {
                    if (result.codeResult) {
                        setScannedBarcode(result.codeResult.code);
                    }
                });

            } catch (err) {
                console.error("Error starting Quagga:", err);
                alert('Error al iniciar el escáner: ' + err.message);
            }

        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Error al acceder a la cámara: ' + error.message);
        }
    };

    const stopScanning = () => {
        if (isScanning) {
            try {
                Quagga.stop();
            } catch (err) {
                console.error("Error stopping Quagga:", err);
            }
            setIsScanning(false);
            
            if (videoRef.current && videoRef.current.srcObject) {
                const tracks = videoRef.current.srcObject.getTracks();
                tracks.forEach(track => track.stop());
                videoRef.current.srcObject = null;
            }
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            setImageSrc(event.target.result);

            try {
                const result = await Quagga.decodeSingle({
                    decoder: {
                        readers: [
                            "ean_reader",
                            "ean_8_reader",
                            "code_128_reader",
                            "code_39_reader",
                            "upc_reader",
                            "upc_e_reader",
                            "codabar_reader",
                            "i2of5_reader"
                        ],
                        multiple: false
                    },
                    locate: true,
                    src: event.target.result,
                    numOfWorkers: navigator.hardwareConcurrency || 4,
                    inputStream: {
                        size: 1600,
                        singleChannel: false
                    },
                    locator: {
                        patchSize: "large",
                        halfSample: false
                    },
                    debug: {
                        showCanvas: true,
                        showPatches: true,
                        showFoundPatches: true,
                        showSkeleton: true,
                        showLabels: true,
                        showPatchLabels: true,
                        showRemainingPatchLabels: true,
                        boxFromPatches: {
                            showTransformed: true,
                            showTransformedBox: true,
                            showBB: true
                        }
                    }
                });

                if (result && result.codeResult) {
                    console.log("Código detectado:", result.codeResult.code);
                    setScannedBarcode(result.codeResult.code);
                } else {
                    console.log("No se detectó código de barras");
                    setScannedBarcode('');
                    alert("No se detectó ningún código de barras. Por favor, intente de nuevo con una imagen más clara.");
                }
            } catch (error) {
                console.error('Error al procesar la imagen:', error);
                setScannedBarcode('');
                alert("Error al procesar la imagen. Por favor, asegúrese de que la imagen sea clara y contenga un código de barras válido.");
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
            const token = authStore.getToken();
            console.log('Token almacenado:', token ? 'Token presente' : 'No hay token'); // Debug log
            
            if (!token) {
                throw new Error('No hay sesión activa. Por favor, inicie sesión nuevamente.');
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
                dispositivo: formData.dispositivo,  // Enviamos el ID del tipo tal cual viene del selector
                modelo: formData.modelo,
                descripcion: formData.descripcion || '',
                cantidad: cantidad,
                purchase_date: new Date().toISOString().split('T')[0],
                location: 'default'
            };

            console.log('Enviando datos al servidor:', requestData);
            console.log('Headers de la petición:', {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            });

            const response = await fetch('http://localhost:5000/api/stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                credentials: 'include',
                mode: 'cors',
                body: JSON.stringify(requestData)
            });

            const textResponse = await response.text();
            console.log('Respuesta del servidor (texto):', textResponse);
            
            let data;
            try {
                data = JSON.parse(textResponse);
                console.log('Respuesta del servidor (parseada):', data);
            } catch (parseError) {
                console.error('Error parsing response:', textResponse);
                throw new Error('Error en el servidor: Respuesta no válida');
            }

            if (!response.ok) {
                const errorMessage = data.error || data.message || 'Error desconocido';
                if (response.status === 401) {
                    // Mostrar el mensaje de error antes de redirigir
                    alert(`Error de autenticación: ${errorMessage}`);
                    console.log('Error de autenticación - redirigiendo a login');
                    localStorage.removeItem('jwt_token');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000); // Esperar 2 segundos antes de redirigir
                    return;
                }
                throw new Error(errorMessage);
            }

            // Éxito - limpiar el formulario
            setScannedBarcode('');
            setFormData({
                inventario: '',
                dispositivo: '',
                modelo: '',
                descripcion: '',
                cantidad: ''
            });
            setImageSrc('');
            alert('Stock guardado exitosamente');

        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    };

    return (
        <section id="nuevo-inventario">
            <h1>Nuevo Inventario</h1>
            
            <div className="scanner-controls">
                <button 
                    className={`scanner-button ${isScanning ? 'scanning' : ''}`}
                    onClick={isScanning ? stopScanning : startScanning}
                >
                    {isScanning ? <><FaStop /> Detener Escáner</> : <><FaCamera /> Iniciar Escáner</>}
                </button>
                
                <div className="file-upload">
                    <label htmlFor="image-input">
                        <FaBarcode /> Cargar imagen de código
                    </label>
                    <input 
                        type="file" 
                        id="image-input" 
                        accept="image/*" 
                        onChange={handleImageChange}
                        style={{ display: 'none' }}
                    />
                </div>
            </div>

            <div className="scanner-container">
                <div className="viewport" style={{ display: isScanning ? 'block' : 'none' }}>
                    <video 
                        ref={videoRef}
                        playsInline
                        autoPlay
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                        }}
                    ></video>
                </div>
                {!isScanning && imageSrc && (
                    <img 
                        id="uploaded-image" 
                        src={imageSrc} 
                        alt="Uploaded" 
                        style={{
                            maxWidth: '100%',
                            maxHeight: '100%',
                            objectFit: 'contain'
                        }}
                    />
                )}
            </div>

            <div className="form-container">
                <input 
                    type="text" 
                    id="scanned-barcode" 
                    placeholder="Código escaneado" 
                    value={scannedBarcode} 
                    readOnly 
                    className="barcode-input"
                />
                
                <div className="form-grid">
                    <input 
                        type="text" 
                        id="inventario" 
                        placeholder="Inventario" 
                        value={formData.inventario} 
                        onChange={handleInputChange} 
                    />
                    <div className="form-group">
                        <label htmlFor="dispositivo">Dispositivo</label>
                        <DeviceTypeSelector
                            value={formData.dispositivo}
                            onChange={handleDeviceTypeChange}
                        />
                    </div>
                    <input 
                        type="text" 
                        id="modelo" 
                        placeholder="Modelo" 
                        value={formData.modelo} 
                        onChange={handleInputChange} 
                    />
                    <input 
                        type="text" 
                        id="descripcion" 
                        placeholder="Descripción" 
                        value={formData.descripcion} 
                        onChange={handleInputChange} 
                    />
                    <input 
                        type="number" 
                        id="cantidad" 
                        placeholder="Cantidad" 
                        value={formData.cantidad} 
                        onChange={handleInputChange} 
                    />
                </div>

                <button 
                    className="save-button" 
                    onClick={handleSaveToServer}
                    disabled={!scannedBarcode || !formData.inventario || !formData.cantidad}
                >
                    {isEditing ? "Actualizar" : "Guardar"}
                </button>
            </div>

            <h2>Inventario Guardado</h2>
            <table>
                <thead>
                    <tr>
                        <th>Barcode</th>
                        <th>Inventario</th>
                        <th>Dispositivo</th>
                        <th>Modelo</th>
                        <th>Descripcion</th>
                        <th>Cantidad</th>
                        <th>Fecha y Hora</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row) => (
                        <tr key={row.id}>
                            <td>{row.barcode}</td>
                            <td>{row.inventario}</td>
                            <td>{row.dispositivo}</td>
                            <td>{row.modelo}</td>
                            <td>{row.descripcion}</td>
                            <td>{row.cantidad}</td>
                            <td>{row.dateAdded}</td>
                            <td>
                                <FaPencilAlt onClick={() => handleEdit(row.id)} style={{ cursor: 'pointer', marginRight: '10px' }} />
                                <FaTrash onClick={() => handleDelete(row.id)} style={{ cursor: 'pointer' }} />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </section>
    );
};

export default NewInventory;
