import { useEffect, useState } from "react";
import {
  AreaChart, Area, ReferenceLine, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";
import api from "../api/client";

export default function Analyses() {
  const [list, setList] = useState<any[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [evo, setEvo] = useState<any>(null);

  useEffect(() => {
    api.get("/api/reports/all-analyses").then((r) => {
      const items = r.data.analyses || [];
      setList(items);
      if (items.length) setSelected(items[0].name);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selected) return;
    api.get(`/api/reports/evolution/${encodeURIComponent(selected)}`)
      .then((r) => setEvo(r.data)).catch(() => setEvo(null));
  }, [selected]);

  const exportExcel = async () => {
    const r = await api.get("/api/reports/export/excel", { responseType: "blob" });
    const url = URL.createObjectURL(r.data);
    const a = document.createElement("a");
    a.href = url; a.download = "mes_analyses.xlsx"; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="flex-between">
        <h1 className="page-title">Analyses</h1>
        <button onClick={exportExcel}>Exporter Excel</button>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "260px 1fr" }}>
        <div className="card" style={{ maxHeight: 500, overflow: "auto" }}>
          <h3 style={{ marginBottom: 12 }}>Mes analyses</h3>
          {list.map((a) => (
            <div key={a.name} onClick={() => setSelected(a.name)}
              style={{
                padding: "10px 12px", borderRadius: 8, cursor: "pointer",
                marginBottom: 4, background: selected === a.name ? "#eef3fb" : "transparent",
                fontWeight: selected === a.name ? 600 : 400,
              }}>
              {a.name} <span className="muted">({a.count})</span>
            </div>
          ))}
          {!list.length && <p className="muted">Aucune analyse.</p>}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Evolution : {selected || "—"}</h3>
          {evo?.points?.length ? (<>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={evo.points}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" fontSize={12} />
                <YAxis />
                <Tooltip />
                {evo.ref_min != null &&
                  <ReferenceLine y={evo.ref_min} stroke="#2563eb" strokeDasharray="4 4"
                    label={{ value: "min", fontSize: 11 }} />}
                {evo.ref_max != null &&
                  <ReferenceLine y={evo.ref_max} stroke="#dc2626" strokeDasharray="4 4"
                    label={{ value: "max", fontSize: 11 }} />}
                <Area type="monotone" dataKey="value" stroke="#1f4e78"
                  fill="#a9cce3" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
            <div className="grid grid-4 mt">
              <div><span className="muted">Min</span><br /><strong>{evo.min}</strong></div>
              <div><span className="muted">Max</span><br /><strong>{evo.max}</strong></div>
              <div><span className="muted">Moyenne</span><br /><strong>{evo.avg}</strong></div>
              <div><span className="muted">Points</span><br /><strong>{evo.points.length}</strong></div>
            </div>
          </>) : <p className="muted">Selectionnez une analyse avec un historique.</p>}
        </div>
      </div>
    </div>
  );
}
