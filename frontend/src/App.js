import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Layout/Header";
import Navigation from "./components/Layout/Navigation";
import Chat from "./pages/Chat";
import Products from "./pages/Products";
import Outlets from "./pages/Outlets";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <Navigation />
        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<Chat />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/products" element={<Products />} />
              <Route path="/outlets" element={<Outlets />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
