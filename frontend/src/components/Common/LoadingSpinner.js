import React from "react";
import "./LoadingSpinner.css";

const LoadingSpinner = ({ size = "medium", text = "Loading..." }) => {
  return (
    <div className={`loading-spinner ${size}`}>
      <div className="spinner"></div>
      <span className="loading-text">{text}</span>
    </div>
  );
};

export default LoadingSpinner;
