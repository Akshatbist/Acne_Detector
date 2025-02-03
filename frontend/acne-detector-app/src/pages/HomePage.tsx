import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../assets/styles.css";

const HomePage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [detections, setDetections] = useState<any[]>([]);
  const [imageURL, setImageURL] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
      setDetections([]); // Clear previous detections
      setImageURL(null); // Clear previous image
    }
  };

  const determineTreatment = (acneTypes: string[]) => {
    const treatmentMap: { [key: string]: string } = {
      Whiteheads: "Topical Retinoid or Benzoyl Peroxide",
      Blackheads: "Salicylic Acid or Retinoid",
      Papules: "Topical Antibiotics or Benzoyl Peroxide",
      Pustules: "Topical Antibiotics or Oral Antibiotics",
      Nodules: "Oral Antibiotics or Isotretinoin",
      "Post-Inflammatory Hyperpigmentation":
        "Laser Therapy or Topical Treatments",
      Scarring: "Laser Treatment or Chemical Peels",
    };

    const treatments = acneTypes.map(
      (acneType) => treatmentMap[acneType] || "Unknown Treatment"
    );

    return treatments.join(", ");
  };

  const handleSubmit = async () => {
    if (file) {
      const formData = new FormData();
      formData.append("file", file);

      setLoading(true);

      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/upload/",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        // Set detections and image URL
        const newDetections = response.data.detections;
        setDetections(newDetections);
        setImageURL(`http://127.0.0.1:8000${response.data.image_url}`);

        // Extract acne types from the detections
        const acneTypes = newDetections
          .map((d: { class_name: string }) => d.class_name)
          .join(", "); // Converts all detected acne types into a string

        const acneTypeList = newDetections.map(
          (d: { class_name: string }) => d.class_name
        ); // Get acne types as an array
        const treatment = determineTreatment(acneTypeList);

        navigate("/results", {
          state: {
            acnetypes: acneTypes, // Use acneTypes directly
            treatment: treatment,
            imageURL: `http://127.0.0.1:8000${response.data.image_url}`,
          },
        });
      } catch (error) {
        console.error("Error uploading image:", error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="homepage">
      <div className="card">
        <h1 className="heading">Acne Detector</h1>
        <input type="file" onChange={handleFileChange} className="file-input" />
        <button
          onClick={handleSubmit}
          className="submit-btn"
          disabled={loading}
        >
          {loading ? "Processing...." : "Submit"}
        </button>
        {/* Show Loading Indicator */}
        {loading && <p className="loading-text">Processing... Please wait.</p>}

        {/* Display Detections */}
        {detections.length > 0 && (
          <div className="detections">
            <h2 className="detections-heading">Detections:</h2>
            <pre className="detections-pre">
              {JSON.stringify(detections, null, 2)}
            </pre>
          </div>
        )}

        {/* Display Processed Image */}
        {imageURL && (
          <div className="image-result">
            <h2>Processed Image:</h2>
            <img
              src={imageURL}
              alt="Processed result"
              className="processed-img"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
