// import React, { useState } from 'react';
// import Quagga from 'quagga'; // Importar QuaggaJS

// const NewInventory = () => {
//     const [scannedBarcode, setScannedBarcode] = useState('');
//     const [imageSrc, setImageSrc] = useState('');

//     const handleImageChange = (e) => {
//         const file = e.target.files[0];
//         const reader = new FileReader();

//         reader.onload = function(event) {
//             setImageSrc(event.target.result);

//             // Procesar la imagen cuando esté completamente cargada
//             const img = new Image();
//             img.src = event.target.result;
//             img.onload = function() {
//                 console.log('Image loaded, starting barcode detection...');

//                 Quagga.decodeSingle({
//                     src: img.src,
//                     numOfWorkers: 0,
//                     inputStream: {
//                         size: 800,
//                         singleChannel: false
//                     },
//                     locator: {
//                         patchSize: "x-large",
//                         halfSample: true
//                     },
//                     decoder: {
//                         readers: [
//                             "code_128_reader",
//                             "ean_reader",
//                             "ean_8_reader",
//                             "code_39_reader",
//                             "code_39_vin_reader",
//                             "codabar_reader",
//                             "upc_reader",
//                             "upc_e_reader",
//                             "i2of5_reader",
//                             "2of5_reader",
//                             "code_93_reader"
//                         ]
//                     },
//                     locate: true
//                 }, function(result) {
//                     console.log('Quagga processing result:', result);
//                     if (result && result.codeResult) {
//                         console.log('Barcode detected:', result.codeResult.code);
//                         setScannedBarcode(result.codeResult.code);
//                     } else {
//                         console.log('No barcode detected');
//                         setScannedBarcode('');
//                         alert("No barcode detected. Please try again.");
//                     }
//                 });

//                 console.log('Quagga decodeSingle function called.');
//             };

//             img.onerror = function() {
//                 console.error('Error loading image');
//                 setScannedBarcode('');
//                 alert("Error loading image. Please try again.");
//             };
//         };

//         reader.onerror = function() {
//             console.error('Error reading file');
//             setScannedBarcode('');
//             alert("Error reading file. Please try again.");
//         };

//         reader.readAsDataURL(file);
//     };

//     return (
//         <section id="nuevo-inventario">
//             <h1>Nuevo Inventario</h1>
//             <input type="file" id="image-input" accept="image/*" onChange={handleImageChange} />
//             <br /><br />
//             <img id="uploaded-image" src={imageSrc} alt="Uploaded" />
//             <br /><br />
//             <input type="text" id="scanned-barcode" placeholder="Scanned Barcode" value={scannedBarcode} readOnly />
//             <input type="text" id="inventario" placeholder="Inventario" />
//             <input type="text" id="dispositivo" placeholder="Dispositivo" />
//             <input type="text" id="modelo" placeholder="Modelo" />
//             <input type="number" id="cantidad" placeholder="Cantidad" />
//             <button id="save-button">Guardar</button>
//         </section>
//     );
// };

// export default NewInventory;
