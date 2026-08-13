import { useEffect, useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function Documents() {
  const [docs, setDocs] = useState<any[]>([]);
  const [filter, setFilter] = useState("ALL");
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const nav = useNavigate();

  const load = () => api.get("/api/documents/").then((r) => setDocs(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const onDrop = useCallback(async (files: File[]) => {
    if (!files.length) return;
    setUploading(true); setProgress(0);
    const form = new FormData();
    form.append("file", files[0]);
    try {
      await api.post("/api/documents/upload", form, {
        onUploadProgress: (e) =>
          setProgress(Math.round((e.loaded * 100) / (e.total || 1))),
      });
      await load();
    } catch (e: any) {
      alert(e.response?.data?.detail || "Echec de l'upload");
    } finally { setUploading(false); setProgress(0); }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [], "image/jpeg": [], "image/png": [] },
    maxSize: 20 * 1024 * 1024, multiple: false,
  });

  const del = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Supprimer ce document ?")) return;
    await api.delete(`/api/documents/${id}`); load();
  };

  const shown = docs.filter((d) => filter === "ALL" || d.status === filter);

  return (
    <div>
      <h1 className="page-title">Documents</h1>

      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        {isDragActive ? <p>Deposez le fichier ici...</p>
          : <p>Glissez-deposez un PDF/JPG/PNG (max 20 MB) ou cliquez pour choisir</p>}
        {uploading && <div className="progress"><div style={{ width: `${progress}%` }} /></div>}
      </div>

      <div className="card">
        <div className="flex-between" style={{ marginBottom: 16 }}>
          <h3>Mes documents ({shown.length})</h3>
          <select style={{ width: 200 }} value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="ALL">Tous les statuts</option>
            <option value="PENDING">En attente</option>
            <option value="OCR_DONE">OCR termine</option>
            <option value="AI_DONE">Analyse terminee</option>
            <option value="ERROR">Erreur</option>
          </select>
        </div>
        <table>
          <thead><tr><th>Nom</th><th>Type</th><th>Taille</th><th>Statut</th><th>Date</th><th></th></tr></thead>
          <tbody>
            {shown.map((d) => (
              <tr key={d.id} style={{ cursor: "pointer" }} onClick={() => nav(`/documents/${d.id}`)}>
                <td>{d.original_name}</td>
                <td>{d.doc_type}</td>
                <td>{d.file_size < 1048576
                  ? `${Math.max(1, Math.round(d.file_size / 1024))} KB`
                  : `${(d.file_size / 1024 / 1024).toFixed(2)} MB`}</td>
                <td><span className={`badge ${d.status}`}>{d.status}</span></td>
                <td>{new Date(d.created_at).toLocaleDateString()}</td>
                <td><button style={{ background: "#dc2626" }} onClick={(e) => del(d.id, e)}>Suppr.</button></td>
              </tr>
            ))}
            {!shown.length && <tr><td colSpan={6} className="muted">Aucun document.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
