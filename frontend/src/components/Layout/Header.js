import React from "react";
import "./Header.css";

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <h1>☕ Zus Coffee Assistant</h1>
          </div>
          <div className="header-subtitle">
            Your AI-powered coffee companion
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
