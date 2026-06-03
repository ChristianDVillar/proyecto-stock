import React, { useState, useEffect, useRef } from 'react';
import Quagga from '@ericblade/quagga2';
import { BrowserMultiFormatReader } from '@zxing/browser';
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
        cantidad: '',
        expiration_date: '',
        batch_number: '',
        minimum_stock: '',
        optimal_stock: '',
        unit_cost: '',
        serial_number: '',
        mac_address: '',
        hostname: '',
        warranty_expiry: '',
        contains_gluten: false,
        contains_milk: false,
        contains_nuts: false,
        contains_soy: false,
        supplier_id: '',
    });
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [suppliers, setSuppliers] = useState([]);
    const [rows, setRows] = useState([]);
    const [isEditing, setIsEditing] = useState(false);
    const [, setEditRowId] = useState(null);

    const BARCODE_READERS = [
        "ean_reader", "ean_8_reader", "code_128_reader", "code_39_reader",
        "upc_reader", "upc_e_reader", "codabar_reader", "i2of5_reader"
    ];

    useEffect(() => {
        if (!showAdvanced) return;
        const token = authStore.getToken();
        if (!token) return;
        fetch('/api/suppliers', {
            headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
        })
            .then((r) => (r.ok ? r.json() : { suppliers: [] }))
            .then((d) => setSuppliers(d.suppliers || []))
            .catch(() => setSuppliers([]));
    }, [showAdvanced]);

    useEffect(() => {
        const video = videoRef.current;
        return () => {
            try {
                Quagga.stop();
            } catch (err) {
                console.error("Error stopping Quagga:", err);
            }
            if (video && video.srcObject) {
                const tracks = video.srcObject.getTracks();
                tracks.forEach(track => track.stop());
                video.srcObject = null;
            }
        };
    }, []);

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
                    readers: BARCODE_READERS
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

    const scaleImageToDataUrl = (dataUrl, maxSize = 1200) => {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => {
                const w = img.naturalWidth || img.width;
                const h = img.naturalHeight || img.height;
                const scale = maxSize / Math.max(w, h);
                const width = Math.round(w * scale);
                const height = Math.round(h * scale);
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                try {
                    resolve(canvas.toDataURL('image/png'));
                } catch (e) {
                    resolve(dataUrl);
                }
            };
            img.onerror = () => resolve(dataUrl);
            img.src = dataUrl;
        });
    };

    const tryDecodeImage = async (dataUrl) => {
        const configs = [
            { size: 1200, patchSize: "large", halfSample: false, singleChannel: false },
            { size: 1200, patchSize: "medium", halfSample: false, singleChannel: true },
            { size: 800, patchSize: "large", halfSample: true, singleChannel: false },
            { size: 1600, patchSize: "large", halfSample: false, singleChannel: false },
            { size: 800, patchSize: "medium", halfSample: false, singleChannel: false },
            { size: 600, patchSize: "medium", halfSample: true, singleChannel: true },
            { size: 1000, patchSize: "large", halfSample: false, singleChannel: true }
        ];

        const runDecode = async (src) => {
            for (const { size, patchSize, halfSample, singleChannel } of configs) {
                try {
                    const result = await Quagga.decodeSingle({
                        decoder: {
                            readers: BARCODE_READERS,
                            multiple: false
                        },
                        locate: true,
                        src,
                        numOfWorkers: 0,
                        inputStream: {
                            size,
                            singleChannel: !!singleChannel
                        },
                        locator: {
                            patchSize: patchSize || "medium",
                            halfSample: !!halfSample
                        }
                    });
                    if (result && result.codeResult && result.codeResult.code) {
                        return result.codeResult.code;
                    }
                } catch (_) {
                    continue;
                }
            }
            return null;
        };

        let code = await runDecode(dataUrl);
        if (code) return code;

        const scaled1200 = await scaleImageToDataUrl(dataUrl, 1200);
        if (scaled1200 !== dataUrl) {
            code = await runDecode(scaled1200);
            if (code) return code;
        }

        const scaled800 = await scaleImageToDataUrl(dataUrl, 800);
        if (scaled800 !== dataUrl) {
            code = await runDecode(scaled800);
            if (code) return code;
        }

        // Motor alternativo: ZXing (suele detectar mejor en algunas imágenes)
        code = await tryDecodeWithZXing(dataUrl);
        if (code) return code;
        code = await tryDecodeWithZXing(scaled1200 || dataUrl);
        if (code) return code;
        code = await tryDecodeWithZXing(scaled800 || dataUrl);
        if (code) return code;

        return null;
    };

    const tryDecodeWithZXing = async (dataUrl) => {
        if (!dataUrl) return null;
        try {
            const codeReader = new BrowserMultiFormatReader();
            const result = await codeReader.decodeFromImageUrl(dataUrl);
            if (result && result.getText()) {
                return result.getText().trim();
            }
        } catch (_) {
            // ZXing lanza si no encuentra código; ignorar
        }
        return null;
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            const dataUrl = event.target.result;
            setImageSrc(dataUrl);

            try {
                const code = await tryDecodeImage(dataUrl);
                if (code) {
                    setScannedBarcode(code);
                } else {
                    setScannedBarcode('');
                    alert("No se detectó ningún código de barras. Sugerencias: use una imagen clara, con buen contraste y el código bien enfocado; pruebe recortar la imagen solo al código.");
                }
            } catch (error) {
                console.error('Error al procesar la imagen:', error);
                setScannedBarcode('');
                alert("Error al procesar la imagen. Asegúrese de que el archivo sea una imagen válida (JPG/PNG) con un código de barras visible.");
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

            const trim = (v) => (v != null && typeof v === 'string' ? v.trim() : '');
            const inventario = trim(formData.inventario);
            const modelo = trim(formData.modelo);
            const descripcion = trim(formData.descripcion);
            const dispositivo = trim(formData.dispositivo);

            if (!scannedBarcode || !inventario || !dispositivo || !modelo) {
                throw new Error('Por favor, complete todos los campos requeridos (inventario, dispositivo, modelo).');
            }

            const cantidad = parseInt(formData.cantidad, 10);
            if (isNaN(cantidad) || cantidad <= 0) {
                throw new Error('La cantidad debe ser un número mayor que 0.');
            }

            const requestData = {
                barcode: scannedBarcode.trim(),
                inventario,
                dispositivo,
                modelo,
                descripcion: descripcion || '',
                cantidad,
                purchase_date: new Date().toISOString().split('T')[0],
                location: 'default',
                expiration_date: formData.expiration_date || undefined,
                batch_number: formData.batch_number || undefined,
                minimum_stock: formData.minimum_stock ? parseInt(formData.minimum_stock, 10) : undefined,
                optimal_stock: formData.optimal_stock ? parseInt(formData.optimal_stock, 10) : undefined,
                unit_cost: formData.unit_cost ? parseFloat(formData.unit_cost) : undefined,
                serial_number: formData.serial_number || undefined,
                mac_address: formData.mac_address || undefined,
                hostname: formData.hostname || undefined,
                warranty_expiry: formData.warranty_expiry || undefined,
                contains_gluten: formData.contains_gluten,
                contains_milk: formData.contains_milk,
                contains_nuts: formData.contains_nuts,
                contains_soy: formData.contains_soy,
                supplier_id: formData.supplier_id ? parseInt(formData.supplier_id, 10) : undefined,
            };

            console.log('Enviando datos al servidor:', requestData);
            console.log('Headers de la petición:', {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            });

            const response = await fetch('/api/stock', {
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
                cantidad: '',
                expiration_date: '',
                batch_number: '',
                minimum_stock: '',
                optimal_stock: '',
                unit_cost: '',
                serial_number: '',
                mac_address: '',
                hostname: '',
                warranty_expiry: '',
                contains_gluten: false,
                contains_milk: false,
                contains_nuts: false,
                contains_soy: false,
                supplier_id: '',
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
                    <div className="form-group">
                        <label htmlFor="inventario">Inventario</label>
                        <input 
                            type="text" 
                            id="inventario" 
                            placeholder="Inventario" 
                            value={formData.inventario} 
                            onChange={handleInputChange}
                            className="form-control"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="dispositivo">Dispositivo</label>
                        <DeviceTypeSelector
                            value={formData.dispositivo}
                            onChange={handleDeviceTypeChange}
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="modelo">Modelo</label>
                        <input 
                            type="text" 
                            id="modelo" 
                            placeholder="Modelo" 
                            value={formData.modelo} 
                            onChange={handleInputChange}
                            className="form-control"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="descripcion">Descripción</label>
                        <input 
                            type="text" 
                            id="descripcion" 
                            placeholder="Descripción" 
                            value={formData.descripcion} 
                            onChange={handleInputChange}
                            className="form-control"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="cantidad">Cantidad</label>
                        <input 
                            type="number" 
                            id="cantidad" 
                            placeholder="Cantidad" 
                            value={formData.cantidad} 
                            onChange={handleInputChange}
                            className="form-control"
                            min="1"
                        />
                    </div>
                </div>

                <button type="button" className="toggle-advanced" onClick={() => setShowAdvanced(!showAdvanced)}>
                    {showAdvanced ? '▲ Ocultar campos avanzados' : '▼ Vencimientos, stock mínimo, activos IT, alérgenos'}
                </button>

                {showAdvanced && (
                    <div className="form-grid advanced-fields">
                        <div className="form-group">
                            <label htmlFor="supplier_id">Proveedor</label>
                            <select id="supplier_id" value={formData.supplier_id} onChange={handleInputChange} className="form-control">
                                <option value="">Sin proveedor</option>
                                {suppliers.map((s) => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="form-group">
                            <label htmlFor="expiration_date">Fecha vencimiento</label>
                            <input type="date" id="expiration_date" value={formData.expiration_date} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="batch_number">Nº lote</label>
                            <input type="text" id="batch_number" value={formData.batch_number} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="minimum_stock">Stock mínimo</label>
                            <input type="number" id="minimum_stock" value={formData.minimum_stock} onChange={handleInputChange} className="form-control" min="0" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="optimal_stock">Stock óptimo</label>
                            <input type="number" id="optimal_stock" value={formData.optimal_stock} onChange={handleInputChange} className="form-control" min="0" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="unit_cost">Coste unitario (€)</label>
                            <input type="number" step="0.01" id="unit_cost" value={formData.unit_cost} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="serial_number">Nº serie</label>
                            <input type="text" id="serial_number" value={formData.serial_number} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="mac_address">MAC</label>
                            <input type="text" id="mac_address" value={formData.mac_address} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="hostname">Hostname</label>
                            <input type="text" id="hostname" value={formData.hostname} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="warranty_expiry">Fin garantía</label>
                            <input type="date" id="warranty_expiry" value={formData.warranty_expiry} onChange={handleInputChange} className="form-control" />
                        </div>
                        <div className="form-group allergens">
                            <label>Alérgenos</label>
                            <label><input type="checkbox" checked={formData.contains_gluten} onChange={(e) => setFormData(p => ({ ...p, contains_gluten: e.target.checked }))} /> Gluten</label>
                            <label><input type="checkbox" checked={formData.contains_milk} onChange={(e) => setFormData(p => ({ ...p, contains_milk: e.target.checked }))} /> Lácteos</label>
                            <label><input type="checkbox" checked={formData.contains_nuts} onChange={(e) => setFormData(p => ({ ...p, contains_nuts: e.target.checked }))} /> Frutos secos</label>
                            <label><input type="checkbox" checked={formData.contains_soy} onChange={(e) => setFormData(p => ({ ...p, contains_soy: e.target.checked }))} /> Soja</label>
                        </div>
                    </div>
                )}

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
