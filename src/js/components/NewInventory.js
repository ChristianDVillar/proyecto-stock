import React, { useState } from 'react';
import Quagga from 'quagga'; // Importar QuaggaJS
import { FaTrash, FaPencilAlt } from 'react-icons/fa'; // Importar íconos

const NewInventory = () => {
    const [scannedBarcode, setScannedBarcode] = useState('');
    const [imageSrc, setImageSrc] = useState('');
    const [formData, setFormData] = useState({
        inventario: '',
        dispositivo: '',
        modelo: '',
        cantidad: ''
    });
    const [rows, setRows] = useState([]);
    const [isEditing, setIsEditing] = useState(false);
    const [editRowId, setEditRowId] = useState(null);

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
                        readers: ["code_128_reader","ean_reader"]
                    },
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
            cantidad: row.cantidad === "S/N" ? '' : row.cantidad
        });
        setIsEditing(true);
        setEditRowId(id);
    };

    return (
        <section id="nuevo-inventario">
            <h1>Nuevo Inventario</h1>
            <input type="file" id="image-input" accept="image/*" onChange={handleImageChange} />
            <br /><br />
            <img id="uploaded-image" src={imageSrc} alt="Uploaded" />
            <br /><br />
            <input type="text" id="scanned-barcode" placeholder="Scanned Barcode" value={scannedBarcode} readOnly />
            <input type="text" id="inventario" placeholder="Inventario" value={formData.inventario} onChange={handleInputChange} />
            <input type="text" id="dispositivo" placeholder="Dispositivo" value={formData.dispositivo} onChange={handleInputChange} />
            <input type="text" id="modelo" placeholder="Modelo" value={formData.modelo} onChange={handleInputChange} />
            <input type="number" id="cantidad" placeholder="Cantidad" value={formData.cantidad} onChange={handleInputChange} />
            <button id="save-button" onClick={handleSave}>
                {isEditing ? "Actualizar" : "Guardar"}
            </button>

            <h2>Inventario Guardado</h2>
            <table>
                <thead>
                    <tr>
                        <th>Barcode</th>
                        <th>Inventario</th>
                        <th>Dispositivo</th>
                        <th>Modelo</th>
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
