import React, { useState, useEffect } from "react";
import Header from "./js/components/Header";
import Login from "./js/components/Login";
import NewInventory from "./js/components/NewInventory";
import ConsultInventory from "./js/components/ConsultInventory";
import Footer from "./js/components/Footer";
import authStore from './stores/AuthStore';

import "./styles/Header.css";
import "./styles/styles.css";

function App() {
    // Estado para manejar si el usuario está logueado
    const [isLoggedIn, setIsLoggedIn] = useState(authStore.isLoggedIn());

    useEffect(() => {
        // Función que se ejecutará cuando cambie el estado de autenticación en el AuthStore
        const handleAuthChange = () => setIsLoggedIn(authStore.isLoggedIn());

        // Suscribirse al evento de cambio en AuthStore
        authStore.on('change', handleAuthChange);

        // Limpiar el efecto quitando el listener cuando el componente se desmonte
        return () => authStore.removeListener('change', handleAuthChange);
    }, []);

    return (
        <div>
            <Header />
            {/* Mostrar Login si no está logueado, sino mostrar el contenido principal */}
            {!isLoggedIn ? (
                <Login />
            ) : (
                <>
                    <NewInventory />
                    <ConsultInventory />
                </>
            )}
            <Footer />
        </div>
    );
}

export default App;
