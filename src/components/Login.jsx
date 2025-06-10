import React, { useState, useEffect } from 'react';
import authStore from '../services/AuthStore';
import '../assets/styles/Login.css';

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Solo redirigir si estamos en /login y ya estamos autenticados
        if (window.location.pathname === '/login' && authStore.isLoggedIn()) {
            const userType = authStore.getUserType();
            window.location.replace(userType === 'admin' ? '/admin' : '/');
        }
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            if (!isLogin && formData.password !== formData.confirmPassword) {
                setError('Las contraseñas no coinciden');
                setIsLoading(false);
                return;
            }

            const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
            console.log('Iniciando solicitud de autenticación:', {
                endpoint,
                username: formData.username,
                isLogin
            });
            
            const response = await fetch(`http://localhost:5000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: formData.username,
                    password: formData.password
                })
            });

            console.log('Respuesta recibida:', {
                status: response.status,
                ok: response.ok,
                headers: Object.fromEntries(response.headers.entries()),
                contentType: response.headers.get('content-type')
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Respuesta no JSON:', text);
                throw new Error('El servidor no devolvió una respuesta JSON válida');
            }

            const data = await response.json();
            console.log('Datos de respuesta:', {
                success: response.ok,
                hasToken: !!data.access_token,
                hasUser: !!data.user,
                userType: data.user?.user_type,
                authHeader: response.headers.get('Authorization')
            });

            if (!response.ok) {
                throw new Error(data.error || 'Error en la autenticación');
            }

            // Obtener el token del header de Authorization
            const authHeader = response.headers.get('Authorization');
            const token = authHeader ? authHeader.replace('Bearer ', '') : data.access_token;

            if (!token) {
                throw new Error('No se recibió el token de autenticación');
            }

            // Intentar el login con el token recibido
            const loginSuccess = await authStore.login(token, data.user.username, data.user.user_type);
            
            if (!loginSuccess) {
                throw new Error('Error al guardar los datos de autenticación');
            }

            // Verificar que el token sea válido
            const isValid = await authStore.verifyToken();
            if (!isValid) {
                throw new Error('El token recibido no es válido');
            }

            // Redirigir según el tipo de usuario
            window.location.replace(data.user.user_type === 'admin' ? '/admin' : '/');
        } catch (error) {
            console.error('Login error:', error);
            setError(error.message || 'Error en el inicio de sesión');
            // Limpiar el estado de autenticación en caso de error
            await authStore.clearState(true);
        } finally {
            setIsLoading(false);
        }
    };

    const toggleMode = () => {
        setIsLogin(!isLogin);
        setError('');
        setFormData({
            username: '',
            password: '',
            confirmPassword: ''
        });
    };

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleSubmit}>
                <h2>{isLogin ? 'Iniciar Sesión' : 'Registrarse'}</h2>
                
                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                    <label htmlFor="username">Usuario:</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleInputChange}
                        required
                        disabled={isLoading}
                    />
                </div>
                
                <div className="form-group">
                    <label htmlFor="password">Contraseña:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        required
                        disabled={isLoading}
                    />
                </div>
                
                {!isLogin && (
                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirmar Contraseña:</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleInputChange}
                            required
                            disabled={isLoading}
                        />
                    </div>
                )}
                
                <button type="submit" className="submit-button" disabled={isLoading}>
                    {isLoading ? 'Procesando...' : (isLogin ? 'Iniciar Sesión' : 'Registrarse')}
                </button>
                
                <button 
                    type="button" 
                    className="toggle-button" 
                    onClick={toggleMode}
                    disabled={isLoading}
                >
                    {isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
                </button>
            </form>
        </div>
    );
};

export default Login;


