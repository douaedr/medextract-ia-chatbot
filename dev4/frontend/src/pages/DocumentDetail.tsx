import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";

export default function DocumentDetail() {
  const { id } = useParams();
  const [doc, setDoc] = useState<any>(null);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    api.get(`/api/documents/${id}`).then((r) => setDoc(r.data)).catch(() => {});
    api.get(`/api/ai/results/${id}`).then((r) => setResult(r.data)).catch(() => setResult(null));
  }, [id]);

  if (!doc) return <div>Chargement...</div>;

  const confColor = (c: number) =>
    c >= 0.8 ? "#16a34a" : c >= 0.6 ? "#a16207" : "#dc2626";

  return (
    <div>
      <h1 className="page-title">{doc.original_name}</h1>

      <div className="grid grid-2">
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Informations</h3>
          <p className="muted">Type : {doc.doc_type}</p>
          <p className="muted">Statut : <span className={`badge ${doc.status}`}>{doc.status}</span></p>
          <p className="muted">Taille : {doc.file_size < 1048576
            ? `${Math.max(1, Math.round(doc.file_size / 1024))} KB`
            : `${(doc.file_size / 1024 / 1024).toFixed(2)} MB`}</p>
          <p className="muted">Date : {new Date(doc.created_at).toLocaleString()}</p>
          {result && (<>
            <p className="muted mt">Patient : {result.patient_name || "—"}</p>
            <p className="muted">Medecin : {result.doctor_name || "—"}</p>
            <p className="muted">Modele : {result.model_version}</p>
          </>)}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Texte OCR</h3>
          <div style={{ maxHeight: 220, overflow: "auto", fontSize: 13, whiteSpace: "pre-wrap" }}
               className="muted">
            {doc.ocr_text || "OCR en cours ou indisponible..."}
          </div>
        </div>
      </div>

      <div className="card mt">
        <h3 style={{ marginBottom: 12 }}>Analyses extraites</h3>
        <table>
          <thead><tr><th>Analyse</th><th>Valeur</th><th>Unite</th><th>Normes</th><th>Statut</th><th>Confiance</th></tr></thead>
          <tbody>
            {result?.analyses?.map((a: any, i: number) => (
              <tr key={i}>
                <td>{a.analysis_name}</td>
                <td><strong>{a.value}</strong></td>
                <td>{a.unit}</td>
                <td className="muted">{a.ref_min ?? "?"} - {a.ref_max ?? "?"}</td>
                <td><span className={`badge ${a.status}`}>{a.status}</span></td>
                <td style={{ color: confColor(a.confidence), fontWeight: 600 }}>
                  {(a.confidence * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
            {!result?.analyses?.length &&
              <tr><td colSpan={6} className="muted">Analyse IA en cours ou aucune donnee.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
