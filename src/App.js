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
    const [isLoggedIn, setIsLoggedIn] = useState(authStore.isLoggedIn());

    useEffect(() => {
        const handleAuthChange = () => setIsLoggedIn(authStore.isLoggedIn());
        authStore.on('change', handleAuthChange);

        return () => authStore.removeListener('change', handleAuthChange);
    }, []);

    return (
        <div>
            <Header />
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