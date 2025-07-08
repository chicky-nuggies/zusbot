import React from "react";
import { NavLink } from "react-router-dom";
import "./Navigation.css";

const Navigation = () => {
  return (
    <nav className="navigation">
      <div className="container">
        <div className="nav-links">
          <NavLink to="/chat" className="nav-link">
            💬 Chat
          </NavLink>
          <NavLink to="/products" className="nav-link">
            ☕ Products
          </NavLink>
          <NavLink to="/outlets" className="nav-link">
            📍 Outlets
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
