import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../assets/styles.css";

type Detection = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  confidence: number;
  class: number;
  class_name: string;
};

const API_BASE =
  (import.meta as any).env?.VITE_API_URL || "http://127.0.0.1:8000";

const TREATMENT_MAP: Record<string, string> = {
  Whiteheads: "Topical retinoid or benzoyl peroxide",
  Blackheads: "Salicylic acid or retinoid",
  Papules: "Topical antibiotics or benzoyl peroxide",
  Pustules: "Topical antibiotics or oral antibiotics",
  Nodules: "Oral antibiotics or isotretinoin (derm-supervised)",
  Cysts: "Oral antibiotics or isotretinoin (derm-supervised)",
  "Post-Inflammatory Hyperpigmentation":
    "Topical azelaic acid/retinoids; consider lasers/peels (derm)",
  Scarring: "Resurfacing/lasers/microneedling; dermatology consult",
};

function dedupePreserveOrder<T>(arr: T[]): T[] {
  return Array.from(new Set(arr));
}

const HomePage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [imageURL, setImageURL] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      if (imageURL) URL.revokeObjectURL(imageURL);
    };
  }, [imageURL]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    if (imageURL) URL.revokeObjectURL(imageURL);
    setFile(e.target.files[0]);
    setDetections([]);
    setRecommendations([]);
    setImageURL(null);
  };

  const buildRecommendations = (dets: Detection[]) => {
    const classes = dedupePreserveOrder(dets.map((d) => d.class_name));
    const recs = dedupePreserveOrder(
      classes.map(
        (cls) => TREATMENT_MAP[cls] || "General skincare; consider derm consult"
      )
    );
    setRecommendations(recs);
    return { classes, recs };
  };

  const fetchDetectionsJSON = async (formData: FormData) => {
    const jsonResp = await axios.post(`${API_BASE}/detect`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    const dets: Detection[] = jsonResp.data?.detections ?? [];
    setDetections(dets);
    return dets;
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      // 1) Request annotated image (primary)
      const imgResp = await axios.post(
        `${API_BASE}/detect?return_annotated=true`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          responseType: "blob",
        }
      );

      const blobURL = URL.createObjectURL(imgResp.data);
      setImageURL(blobURL);

      // 2) Try to read detections from header (if backend sends X-Detections)
      let dets: Detection[] = [];
      const headerVal = imgResp.headers["x-detections"];
      if (headerVal) {
        try {
          const parsed = JSON.parse(headerVal) as { detections?: Detection[] };
          dets = parsed?.detections ?? [];
          setDetections(dets);
        } catch {
          /* ignore parse errors, fallback below */
        }
      }

      // 3) Fallback to a lightweight JSON call if header missing
      if (dets.length === 0) {
        dets = await fetchDetectionsJSON(formData);
      }

      // 4) Build recommendations from detected classes
      const { classes, recs } = buildRecommendations(dets);

      // (Optional) Route to results page with everything
      navigate("/results", {
        state: {
          acnetypes: classes.join(", "),
          treatment: recs.join(", "),
          imageURL: blobURL,
        },
      });
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="homepage">
      <div className="card">
        <h1 className="heading">Acne Detector</h1>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file-input"
        />

        <button
          onClick={handleSubmit}
          className="submit-btn"
          disabled={loading}
        >
          {loading ? "Processing..." : "Submit"}
        </button>

        {loading && <p className="loading-text">Processing... Please wait.</p>}

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

        {detections.length > 0 && (
          <div className="detections">
            <h2 className="detections-heading">Detections:</h2>
            <pre className="detections-pre">
              {JSON.stringify(detections, null, 2)}
            </pre>
          </div>
        )}

        {recommendations.length > 0 && (
          <div className="recs">
            <h2>Recommendations (not medical advice):</h2>
            <ul>
              {recommendations.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
