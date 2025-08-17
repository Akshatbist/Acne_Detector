import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../assets/styles.css";

const ResultPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { acnetypes, treatment, imageURL } = location.state || {};
  const NoResult = !acnetypes || !treatment;
  const declaimer =
    "Our AI model was trained on a limited dataset and may not recognize all acne types. Please consult a dermatologist for an accurate diagnosis.";

  return (
    <div className="result-container">
      <h2>Detected Acne Type</h2>
      <p>{acnetypes || "Unknown"}</p>

      <h2>Suggested Treatment</h2>
      <p>{treatment || "No recommendation available"}</p>

      {NoResult && <p>{declaimer}</p>}

      {imageURL && (
        <img src={imageURL} alt="Detected Acne" className="result-image" />
      )}

      {/* Back Button in Sticky Footer */}
      <div className="sticky-footer">
        <button className="back-button" onClick={() => navigate(-1)}>
          Go Back
        </button>
      </div>
    </div>
  );
};

export default ResultPage;
