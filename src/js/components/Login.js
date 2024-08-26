import React, { useState } from 'react';
import authStore from '../../stores/AuthStore'; // Asegúrate de que la ruta sea correcta

const Login = () => {
    const [username, setUsername] = useState('');

    const handleLogin = () => {
        if (username) {
            authStore.login(username); // Realiza el login en AuthStore
            console.log("Usuario logueado:", username); // Mostrar el nombre de usuario en consola
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
            <button onClick={handleLogin}>Iniciar Sesión</button>
        </div>
    );
};

export default Login;

