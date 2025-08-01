// AuthStore.js
class AuthStore {
    constructor() {
        if (AuthStore.instance) {
            return AuthStore.instance;
        }
        AuthStore.instance = this;
        
        this._isInitialized = false;
        this._token = null;
        this._userName = '';
        this._userType = '';
        this._isLoggedIn = false;
        this._lastVerification = 0;
        
        // Inicializar inmediatamente desde localStorage
        this.initializeFromStorage();
        
        // Agregar listener para cambios en localStorage
        window.addEventListener('storage', this.handleStorageChange.bind(this));
        
        // Verificar el token periódicamente
        this.startTokenVerification();
    }

    // Sistema de eventos personalizado
    emit(eventName) {
        const event = new CustomEvent('authstore-' + eventName, {
            detail: {
                isLoggedIn: this._isLoggedIn,
                userName: this._userName,
                userType: this._userType,
                hasToken: !!this._token
            }
        });
        window.dispatchEvent(event);
    }

    addEventListener(eventName, callback) {
        window.addEventListener('authstore-' + eventName, callback);
    }

    removeEventListener(eventName, callback) {
        window.removeEventListener('authstore-' + eventName, callback);
    }

    startTokenVerification() {
        // Verificar el token cada 5 minutos
        setInterval(async () => {
            if (this._token) {
                await this.verifyToken();
            }
        }, 5 * 60 * 1000);
    }

    handleStorageChange(event) {
        console.log('Storage change detected:', event);
        if (event.key === 'jwt_token' || event.key === 'username' || event.key === 'user_type') {
            this.initializeFromStorage();
        }
    }

    async initializeFromStorage() {
        try {
            // Get all auth data from storage
            const token = localStorage.getItem('jwt_token');
            const username = localStorage.getItem('username');
            const userType = localStorage.getItem('user_type');

            console.log('Loading auth state from storage:', {
                hasToken: !!token,
                hasUsername: !!username,
                userType,
                tokenPreview: token ? token.substring(0, 10) + '...' : null
            });

            // Clear state if any required data is missing
            if (!token || !username || !userType) {
                console.log('Missing required auth data in storage:', {
                    hasToken: !!token,
                    hasUsername: !!username,
                    hasUserType: !!userType
                });
                await this.clearState(false);
                return;
            }

            // Set instance state
            this._token = token;
            this._userName = username;
            this._userType = userType;
            this._isLoggedIn = true;
            this._isInitialized = true;

            // No verificar el token inmediatamente después de inicializar
            this._lastVerification = Date.now();

            console.log('Auth state loaded successfully:', {
                isLoggedIn: this._isLoggedIn,
                userName: this._userName,
                userType: this._userType,
                hasToken: !!this._token,
                isInitialized: this._isInitialized,
                tokenPreview: this._token ? this._token.substring(0, 10) + '...' : null
            });

            this.emit('change');
        } catch (error) {
            console.error('Error loading auth state:', error);
            await this.clearState(true);
        }
    }

    async verifyToken() {
        if (!this._token) return false;

        // Evitar verificaciones demasiado frecuentes
        const now = Date.now();
        if (now - this._lastVerification < 10000) { // 10 segundos
            return this._isLoggedIn;
        }

        try {
            // Primero, verificar el estado de la sesión
            const debugResponse = await fetch('http://localhost:5000/api/auth/debug', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this._token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            // Si hay un error de red o el servidor no responde, mantener el estado actual
            if (!debugResponse.ok && debugResponse.status !== 401) {
                console.log('Error de red en debug endpoint:', debugResponse.status);
                return this._isLoggedIn;
            }

            // Si recibimos un 401, el token es definitivamente inválido
            if (debugResponse.status === 401) {
                console.log('Token inválido (401 en debug endpoint)');
                await this.clearState(true);
                return false;
            }

            const debugData = await debugResponse.json();
            console.log('Session debug info:', debugData);

            if (!debugData.valid_token) {
                console.log('Token no válido según debug endpoint');
                await this.clearState(true);
                return false;
            }

            // Si el token es válido, obtener datos del usuario
            const response = await fetch('http://localhost:5000/api/auth/me', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this._token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include'
            });

            // Si hay un error de red, mantener el estado actual
            if (!response.ok && response.status !== 401) {
                console.log('Error de red en /me endpoint:', response.status);
                return this._isLoggedIn;
            }

            // Si recibimos un 401, el token es definitivamente inválido
            if (response.status === 401) {
                console.log('Token inválido (401 en /me endpoint)');
                await this.clearState(true);
                return false;
            }

            const data = await response.json();
            this._lastVerification = now;

            // Actualizar datos del usuario si han cambiado
            if (data.username !== this._userName || data.user_type !== this._userType) {
                this._userName = data.username;
                this._userType = data.user_type;
                localStorage.setItem('username', data.username);
                localStorage.setItem('user_type', data.user_type);
                this.emit('change');
            }

            // Verificar y actualizar el token si se recibió uno nuevo
            const newToken = response.headers.get('Authorization')?.replace('Bearer ', '');
            if (newToken && newToken !== this._token) {
                this._token = newToken;
                localStorage.setItem('jwt_token', newToken);
                this.emit('change');
            }

            this._isLoggedIn = true;
            return true;
        } catch (error) {
            console.error('Error verificando token:', error);
            // Solo limpiar el estado si es un error de autenticación
            if (error.message.includes('401') || error.message.includes('unauthorized')) {
                await this.clearState(true);
                return false;
            }
            return this._isLoggedIn; // Mantener el estado actual para otros errores
        }
    }

    async clearState(emitChange = true) {
        console.log('Clearing auth state');
        
        // Clear instance state
        this._token = null;
        this._userName = '';
        this._userType = '';
        this._isLoggedIn = false;
        this._lastVerification = 0;
        
        // Clear storage
        try {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('username');
            localStorage.removeItem('user_type');
        } catch (error) {
            console.error('Error clearing localStorage:', error);
        }
        
        if (emitChange) {
            console.log('Emitting auth state change after clear');
            this.emit('change');
        }
    }

    isLoggedIn() {
        const isValid = this._isLoggedIn && !!this._token;
        console.log('Checking login state:', {
            _isLoggedIn: this._isLoggedIn,
            hasToken: !!this._token,
            isValid,
            lastVerification: new Date(this._lastVerification).toISOString()
        });
        return isValid;
    }

    isAdmin() {
        return this._userType === 'admin';
    }

    getUserName() {
        return this._userName;
    }

    getUserType() {
        return this._userType;
    }

    getToken() {
        if (!this._token) {
            console.log('No token available');
            return null;
        }
        // Devuelve el token con prefijo Bearer, pero no lo guarda así en memoria ni en localStorage
        if (this._token.startsWith('Bearer ')) {
            return this._token;
        }
        return `Bearer ${this._token}`;
    }

    async login(token, username, userType) {
        console.log('Setting login state:', { 
            username, 
            userType, 
            hasToken: !!token,
            tokenPreview: token ? token.substring(0, 10) + '...' : null
        });
        
        if (!token || !username || !userType) {
            console.error('Missing required login data:', {
                hasToken: !!token,
                hasUsername: !!username,
                hasUserType: !!userType
            });
            throw new Error('Missing required login data');
        }

        try {
            // Limpiar el estado anterior sin emitir cambios
            await this.clearState(false);

            // Set instance state
            this._token = token;
            this._userName = username;
            this._userType = userType;
            this._isLoggedIn = true;
            this._lastVerification = Date.now(); // Actualizar la última verificación
            
            // Set storage state
            localStorage.setItem('jwt_token', token);
            localStorage.setItem('username', username);
            localStorage.setItem('user_type', userType);
            
            console.log('Login successful:', {
                isLoggedIn: this._isLoggedIn,
                userName: this._userName,
                userType: this._userType,
                hasToken: !!this._token,
                tokenPreview: this._token ? this._token.substring(0, 10) + '...' : null,
                storage: {
                    token: !!localStorage.getItem('jwt_token'),
                    username: localStorage.getItem('username'),
                    userType: localStorage.getItem('user_type')
                }
            });
            
            // Esperar un momento antes de emitir el cambio
            await new Promise(resolve => setTimeout(resolve, 100));
            this.emit('change');
            return true;
        } catch (error) {
            console.error('Error during login:', error);
            await this.clearState(true);
            throw error;
        }
    }

    async logout(redirect = true) {
        await this.clearState(true);
        if (redirect) {
            window.location.href = '/login';
        }
    }

    validateAuth() {
        if (!this.isLoggedIn()) {
            // Solo limpiar el estado sin redireccionar
            this.clearState(true);
            return false;
        }
        return true;
    }
}

// Create and export a singleton instance
const authStore = new AuthStore();
export default authStore;

