import React, { useState } from "react";
import { productsAPI } from "../services/api";
import LoadingSpinner from "../components/Common/LoadingSpinner";
import ToolMetadata from "../components/Common/ToolMetadata";
import "./Products.css";

const Products = () => {
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
      const response = await productsAPI.searchProducts(query.trim());
      setResult(response);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to search products. Please try again."
      );
      console.error("Products search error:", err);
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
    <div className="products-page">
      <h1 className="page-title">Product Search</h1>
      <p className="page-subtitle">
        Ask about our coffee products, flavors, ingredients, pricing, or
        anything else!
      </p>

      <div className="products-container">
        <div className="search-section">
          <form onSubmit={handleSubmit} className="search-form">
            <div className="form-group">
              <label htmlFor="product-query" className="form-label">
                What would you like to know about our products?
              </label>
              <textarea
                id="product-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="E.g., What coffee drinks do you have with less sugar? Tell me about your iced coffee options. What's the most popular drink?"
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
                {isLoading ? "Searching..." : "Search Products"}
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
                onClick={() =>
                  setQuery("What are your most popular coffee drinks?")
                }
                disabled={isLoading}
              >
                Popular Drinks
              </button>
              <button
                className="suggestion-card"
                onClick={() =>
                  setQuery("Tell me about your iced coffee options")
                }
                disabled={isLoading}
              >
                Iced Coffee
              </button>
              <button
                className="suggestion-card"
                onClick={() => setQuery("What drinks have low sugar content?")}
                disabled={isLoading}
              >
                Low Sugar Options
              </button>
              <button
                className="suggestion-card"
                onClick={() =>
                  setQuery("What's the price range of your beverages?")
                }
                disabled={isLoading}
              >
                Pricing Info
              </button>
            </div>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {isLoading && (
          <div className="loading-section">
            <LoadingSpinner
              size="large"
              text="Searching our product database..."
            />
          </div>
        )}

        {result && (
          <div className="results-section">
            <div className="result-card">
              <h2>AI Product Summary</h2>
              <div className="result-content">
                <div className="query-echo">
                  <strong>Your Query:</strong> {result.query}
                </div>
                <div className="ai-summary">
                  <h3>Summary:</h3>
                  <p>{result.summary}</p>
                </div>

                {result.retrieved_products &&
                  result.retrieved_products.length > 0 && (
                    <div className="retrieved-products">
                      <h3>Related Products Found:</h3>
                      <div className="products-list">
                        {result.retrieved_products.map((product, index) => (
                          <div key={index} className="product-item">
                            <div className="product-header">
                              <span className="product-id">
                                ID: {product.id}
                              </span>
                              <span className="similarity-score">
                                Match:{" "}
                                {(product.similarity_score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="product-content">
                              {product.content}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

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

export default Products;
