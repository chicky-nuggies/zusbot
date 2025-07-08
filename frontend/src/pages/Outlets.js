import React, { useState } from "react";
import { outletsAPI } from "../services/api";
import LoadingSpinner from "../components/Common/LoadingSpinner";
import ToolMetadata from "../components/Common/ToolMetadata";
import "./Outlets.css";

const Outlets = () => {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await outletsAPI.queryOutlets(query.trim());
      setResult(response);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to query outlets. Please try again."
      );
      console.error("Outlets query error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResult(null);
    setQuery("");
    setError(null);
  };

  return (
    <div className="outlets-page">
      <h1 className="page-title">Outlet Finder</h1>
      <p className="page-subtitle">
        Find Zus Coffee outlets by location, opening hours, facilities, or any
        other criteria!
      </p>

      <div className="outlets-container">
        <div className="search-section">
          <form onSubmit={handleSubmit} className="search-form">
            <div className="form-group">
              <label htmlFor="outlet-query" className="form-label">
                What outlets are you looking for?
              </label>
              <textarea
                id="outlet-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="E.g., Find outlets near KLCC, Show me outlets open 24 hours, Which outlets have WiFi?, Outlets in Kuala Lumpur with parking"
                className="form-textarea"
                rows={4}
                disabled={isLoading}
              />
            </div>
            <div className="form-actions">
              <button
                type="submit"
                className="btn"
                disabled={isLoading || !query.trim()}
              >
                {isLoading ? "Searching..." : "Find Outlets"}
              </button>
              {result && (
                <button
                  type="button"
                  onClick={clearResults}
                  className="btn btn-secondary"
                >
                  Clear Results
                </button>
              )}
            </div>
          </form>

          {/* Quick suggestions */}
          <div className="suggestions-section">
            <h3>Quick Suggestions:</h3>
            <div className="suggestions-grid">
              <button
                className="suggestion-card"
                onClick={() => setQuery("Find outlets near KLCC")}
                disabled={isLoading}
              >
                📍 Near KLCC
              </button>
              <button
                className="suggestion-card"
                onClick={() => setQuery("Show me outlets open 24 hours")}
                disabled={isLoading}
              >
                🕐 24 Hour Outlets
              </button>
              <button
                className="suggestion-card"
                onClick={() => setQuery("Which outlets have WiFi?")}
                disabled={isLoading}
              >
                📶 WiFi Available
              </button>
              <button
                className="suggestion-card"
                onClick={() => setQuery("Outlets in Kuala Lumpur with parking")}
                disabled={isLoading}
              >
                🅿️ With Parking
              </button>
              <button
                className="suggestion-card"
                onClick={() => setQuery("Find outlets in shopping malls")}
                disabled={isLoading}
              >
                🏢 In Malls
              </button>
              <button
                className="suggestion-card"
                onClick={() => setQuery("Show all outlets in Selangor")}
                disabled={isLoading}
              >
                🗺️ Selangor Area
              </button>
            </div>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {isLoading && (
          <div className="loading-section">
            <LoadingSpinner
              size="large"
              text="Searching our outlet database..."
            />
          </div>
        )}

        {result && (
          <div className="results-section">
            <div className="result-card">
              <h2>🏪 Outlet Search Results</h2>
              <div className="result-content">
                <div className="query-echo">
                  <strong>Your Query:</strong> {result.query}
                </div>

                <div className="ai-response">
                  <h3>Results:</h3>
                  <div className="response-content">{result.response}</div>
                </div>

                {result.tool_calls && result.tool_calls.length > 0 && (
                  <ToolMetadata toolCalls={result.tool_calls} />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Outlets;
