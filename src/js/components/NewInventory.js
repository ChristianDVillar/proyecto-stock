import React, { useState, useEffect, useRef } from 'react';
import Quagga from 'quagga'; // Importar QuaggaJS
import { FaTrash, FaPencilAlt, FaCamera, FaBarcode, FaStop } from 'react-icons/fa'; // Importar íconos

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

    const startScanning = () => {
        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: videoRef.current,
                constraints: {
                    facingMode: "environment"
                },
            },
            decoder: {
                readers: [
                    "code_128_reader",
                    "ean_reader",
                    "ean_8_reader",
                    "code_39_reader",
                    "code_39_vin_reader",
                    "codabar_reader",
                    "upc_reader",
                    "upc_e_reader",
                    "i2of5_reader"
                ],
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
            }
        }, function(err) {
            if (err) {
                console.error(err);
                alert('Error al iniciar el escáner: ' + err.message);
                return;
            }
            setIsScanning(true);
            Quagga.start();
        });

        Quagga.onDetected((result) => {
            if (result.codeResult) {
                setScannedBarcode(result.codeResult.code);
                // Reproducir un sonido de éxito
                const audio = new Audio('/assets/beep.mp3');
                audio.play();
                
                // Opcional: detener el escaneo después de una lectura exitosa
                // stopScanning();
            }
        });

        Quagga.onProcessed((result) => {
            const drawingCtx = Quagga.canvas.ctx.overlay;
            const drawingCanvas = Quagga.canvas.dom.overlay;

            if (result) {
                if (result.boxes) {
                    drawingCtx.clearRect(0, 0, parseInt(drawingCanvas.getAttribute("width")), parseInt(drawingCanvas.getAttribute("height")));
                    result.boxes.filter(function(box) {
                        return box !== result.box;
                    }).forEach(function(box) {
                        Quagga.ImageDebug.drawPath(box, { x: 0, y: 1 }, drawingCtx, { color: "green", lineWidth: 2 });
                    });
                }

                if (result.box) {
                    Quagga.ImageDebug.drawPath(result.box, { x: 0, y: 1 }, drawingCtx, { color: "#00F", lineWidth: 2 });
                }

                if (result.codeResult && result.codeResult.code) {
                    Quagga.ImageDebug.drawPath(result.line, { x: 'x', y: 'y' }, drawingCtx, { color: 'red', lineWidth: 3 });
                }
            }
        });
    };

    const stopScanning = () => {
        if (isScanning) {
            Quagga.stop();
            setIsScanning(false);
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        const reader = new FileReader();

        reader.onload = function(event) {
            setImageSrc(event.target.result);

            const img = new Image();
            img.src = event.target.result;
            img.onload = function() {
                console.log('Image loaded, starting barcode detection...');

                Quagga.decodeSingle({
                    src: img.src,
                    numOfWorkers: 0,
                    inputStream: {
                        size: 800,
                        singleChannel: false
                    },
                    locator: {
                        patchSize: "x-large",
                        halfSample: true
                    },
                    decoder: {
                        readers: [
                            "code_128_reader",
                            "ean_reader",
                            "ean_8_reader",
                            "code_39_reader",
                            "code_39_vin_reader",
                            "codabar_reader",
                            "upc_reader",
                            "upc_e_reader",
                            "i2of5_reader",
                            "2of5_reader",
                            "code_93_reader"
                        ]
                    }
                    ,
                    locate: true
                }, function(result) {
                    if (result && result.codeResult) {
                        setScannedBarcode(result.codeResult.code);
                    } else {
                        setScannedBarcode('');
                        alert("No barcode detected. Please try again.");
                    }
                });
            };

            img.onerror = function() {
                setScannedBarcode('');
                alert("Error loading image. Please try again.");
            };
        };

        reader.onerror = function() {
            setScannedBarcode('');
            alert("Error reading file. Please try again.");
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
            const response = await fetch('/api/stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    barcode: scannedBarcode,
                    inventario: formData.inventario,
                    dispositivo: formData.dispositivo,
                    modelo: formData.modelo,
                    descripcion: formData.descripcion,
                    cantidad: parseInt(formData.cantidad),
                    stocktype: formData.dispositivo.toLowerCase(),
                    image: imageSrc
                })
            });

            if (!response.ok) {
                throw new Error('Error al guardar en el servidor');
            }

            const data = await response.json();
            handleSave(); // Actualiza la UI local
            alert('Guardado exitosamente en el servidor');
        } catch (error) {
            console.error('Error:', error);
            alert('Error al guardar: ' + error.message);
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
                {isScanning && (
                    <div className="viewport">
                        <video ref={videoRef}></video>
                        <canvas className="drawingBuffer"></canvas>
                    </div>
                )}
                {!isScanning && imageSrc && (
                    <img id="uploaded-image" src={imageSrc} alt="Uploaded" />
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
                    <input 
                        type="text" 
                        id="dispositivo" 
                        placeholder="Dispositivo" 
                        value={formData.dispositivo} 
                        onChange={handleInputChange} 
                    />
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
