import React, { useState } from 'react';
import authStore from '../../stores/AuthStore'; // Asegúrate de que la ruta sea correcta

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState(''); // Nuevo estado para la clave

    const handleLogin = () => {
        if (username && password) {
            authStore.login(username, password); // Realiza el login en AuthStore con usuario y clave
            console.log("Usuario logueado:", username); // Mostrar el nombre de usuario en consola
        } else {
            console.log("Debe ingresar tanto el nombre de usuario como la clave.");
        }
    };

    return (
        <div className="login">
            <h2>Iniciar Sesión</h2>
            <input 
                type="text" 
                placeholder="Nombre de usuario" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
            />
            <input 
                type="password"  // Campo para la clave
                placeholder="Clave" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
            />
            <button onClick={handleLogin}>Iniciar Sesión</button>
        </div>
    );
};

export default Login;


