import React from "react";
import "./ToolMetadata.css";

const ToolMetadata = ({ toolCalls }) => {
  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="tool-metadata">
      <h4 className="tool-metadata-title">🔧 Tool Usage Details</h4>
      <div className="tool-calls">
        {toolCalls.map((toolCall, index) => (
          <div key={index} className="tool-call">
            <div className="tool-call-header">
              <span className="tool-name">
                {toolCall.tool_name || "Unknown Tool"}
              </span>
              <span className="tool-timestamp">
                {new Date().toLocaleTimeString()}
              </span>
            </div>

            {toolCall.arguments && (
              <div className="tool-section">
                <h5>Arguments:</h5>
                <pre className="tool-data">
                  {JSON.stringify(toolCall.arguments, null, 2)}
                </pre>
              </div>
            )}

            {toolCall.result && (
              <div className="tool-section">
                <h5>Result:</h5>
                <div className="tool-result">
                  {typeof toolCall.result === "string" ? (
                    <p>{toolCall.result}</p>
                  ) : Array.isArray(toolCall.result) ? (
                    <div>
                      <p>Found {toolCall.result.length} items:</p>
                      <ul className="result-list">
                        {toolCall.result.slice(0, 3).map((item, idx) => (
                          <li key={idx} className="result-item">
                            {typeof item === "object"
                              ? JSON.stringify(item)
                              : String(item)}
                          </li>
                        ))}
                        {toolCall.result.length > 3 && (
                          <li className="result-more">
                            ... and {toolCall.result.length - 3} more
                          </li>
                        )}
                      </ul>
                    </div>
                  ) : (
                    <pre className="tool-data">
                      {JSON.stringify(toolCall.result, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ToolMetadata;
