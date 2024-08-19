import React from "react";
import Header from "./js/components/Header";
import NewInventory from "./js/components/NewInventory";
import ConsultInventory from "./js/components/ConsultInventory";

import Footer from "./js/components/Footer";
import "./styles/Header.css";
import "./styles/styles.css";

function App() {
  return (
    <div>
      <Header />
      <NewInventory />
      <ConsultInventory />
      <Footer />
    </div>
  );
}

export default App;
