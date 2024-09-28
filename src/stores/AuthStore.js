// AuthStore.js
import { EventEmitter } from 'events';

class AuthStore extends EventEmitter {
    constructor() {
        super();
        this.user = null; // Aquí almacenamos el usuario autenticado
    }

    login(username, password) {
        // Lógica de autenticación (esto es solo un ejemplo)
        if (username === 'admin' && password === 'admin') {
            this.user = username;
            this.emit('change'); // Notificar que ha cambiado el estado de autenticación
        } else {
            console.log("Nombre de usuario o clave incorrectos");
        }
    }

    logout() {
        this.user = null;
        this.emit('change'); // Notificar que el usuario ha cerrado sesión
    }

    getUserName() {
        return this.user;
    }

    isLoggedIn() {
        return this.user !== null; // Devuelve true si hay un usuario autenticado
    }
}

const authStore = new AuthStore();
export default authStore;

