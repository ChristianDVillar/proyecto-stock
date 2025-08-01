import React, { useState, useEffect } from 'react';
import authStore from '../services/AuthStore';

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isRedirecting, setIsRedirecting] = useState(false);

    useEffect(() => {
        const checkAuth = async () => {
            // Solo redirigir si estamos en /login y ya estamos autenticados
            if (window.location.pathname === '/login' && authStore.isLoggedIn()) {
                const userType = authStore.getUserType();
                window.location.replace(userType === 'admin' ? '/admin' : '/');
            }
        };
        checkAuth();
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

            // Obtener el token del header de Authorization o del body
            const authHeader = response.headers.get('Authorization');
            console.log('Token en header:', authHeader);
            console.log('Token en body:', data.access_token);

            let token = null;
            if (authHeader && authHeader.startsWith('Bearer ')) {
                token = authHeader.substring(7);
            } else if (data.access_token) {
                token = data.access_token;
            }

            if (!token) {
                throw new Error('No se recibió el token de autenticación');
            }

            console.log('Token obtenido:', token);

            // Guardar en el store usando el método login
            const loginSuccess = await authStore.login(token, data.user.username, data.user.user_type);
            
            if (!loginSuccess) {
                throw new Error('Error al guardar los datos de autenticación');
            }

            console.log('Autenticación exitosa, redirigiendo...');
            setIsRedirecting(true);

            // Redirigir según el tipo de usuario
            const userType = data.user?.user_type || 'user';
            setTimeout(() => {
                window.location.replace(userType === 'admin' ? '/admin' : '/');
            }, 1000);

        } catch (error) {
            console.error('Error en autenticación:', error);
            setError(error.message || 'Error en la autenticación');
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

    if (isRedirecting) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '100vh',
                backgroundColor: '#f8f9fa'
            }}>
                <div style={{
                    textAlign: 'center',
                    padding: '40px',
                    backgroundColor: '#ffffff',
                    borderRadius: '12px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    border: '1px solid #e9ecef'
                }}>
                    <h2 style={{ color: '#2d3436', marginBottom: '20px' }}>
                        ¡Autenticación Exitosa!
                    </h2>
                    <p style={{ color: '#636e72' }}>
                        Redirigiendo...
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            backgroundColor: '#f8f9fa',
            padding: '20px'
        }}>
            <div style={{
                maxWidth: '400px',
                width: '100%',
                backgroundColor: '#ffffff',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e9ecef',
                padding: '40px'
            }}>
                <div style={{
                    textAlign: 'center',
                    marginBottom: '30px'
                }}>
                    <h2 style={{
                        color: '#6c5ce7',
                        fontSize: '28px',
                        fontWeight: '600',
                        marginBottom: '10px'
                    }}>
                        {isLogin ? 'Iniciar Sesión' : 'Registrarse'}
                    </h2>
                    <p style={{
                        color: '#636e72',
                        fontSize: '14px'
                    }}>
                        {isLogin ? 'Accede a tu cuenta' : 'Crea una nueva cuenta'}
                    </p>
                </div>

                <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Usuario:
                        </label>
                        <input
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleInputChange}
                            required
                            style={{
                                width: '100%',
                                padding: '12px',
                                border: '2px solid #dfe6e9',
                                borderRadius: '8px',
                                fontSize: '14px',
                                outline: 'none',
                                transition: 'border-color 0.3s ease',
                                boxSizing: 'border-box'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                            onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                        />
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#2d3436',
                            fontWeight: '500',
                            fontSize: '14px'
                        }}>
                            Contraseña:
                        </label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            required
                            style={{
                                width: '100%',
                                padding: '12px',
                                border: '2px solid #dfe6e9',
                                borderRadius: '8px',
                                fontSize: '14px',
                                outline: 'none',
                                transition: 'border-color 0.3s ease',
                                boxSizing: 'border-box'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                            onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                        />
                    </div>

                    {!isLogin && (
                        <div style={{ marginBottom: '20px' }}>
                            <label style={{
                                display: 'block',
                                marginBottom: '8px',
                                color: '#2d3436',
                                fontWeight: '500',
                                fontSize: '14px'
                            }}>
                                Confirmar Contraseña:
                            </label>
                            <input
                                type="password"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleInputChange}
                                required
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    border: '2px solid #dfe6e9',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    outline: 'none',
                                    transition: 'border-color 0.3s ease',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#74b9ff'}
                                onBlur={(e) => e.target.style.borderColor = '#dfe6e9'}
                            />
                        </div>
                    )}

                    {error && (
                        <div style={{
                            backgroundColor: 'rgba(225, 112, 85, 0.1)',
                            border: '1px solid #e17055',
                            color: '#e17055',
                            padding: '12px',
                            borderRadius: '8px',
                            marginBottom: '20px',
                            fontSize: '14px'
                        }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading}
                        style={{
                            width: '100%',
                            padding: '14px',
                            backgroundColor: isLoading ? '#636e72' : '#00b894',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            transition: 'background-color 0.3s ease',
                            textTransform: 'uppercase',
                            letterSpacing: '1px'
                        }}
                        onMouseOver={(e) => {
                            if (!isLoading) {
                                e.target.style.backgroundColor = '#00a085';
                            }
                        }}
                        onMouseOut={(e) => {
                            if (!isLoading) {
                                e.target.style.backgroundColor = '#00b894';
                            }
                        }}
                    >
                        {isLoading ? 'Procesando...' : (isLogin ? 'Iniciar Sesión' : 'Registrarse')}
                    </button>
                </form>

                <div style={{
                    textAlign: 'center',
                    paddingTop: '20px',
                    borderTop: '1px solid #e9ecef'
                }}>
                    <button
                        type="button"
                        onClick={toggleMode}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#74b9ff',
                            cursor: 'pointer',
                            fontSize: '14px',
                            textDecoration: 'underline',
                            transition: 'color 0.3s ease'
                        }}
                        onMouseOver={(e) => e.target.style.color = '#0984e3'}
                        onMouseOut={(e) => e.target.style.color = '#74b9ff'}
                    >
                        {isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;


