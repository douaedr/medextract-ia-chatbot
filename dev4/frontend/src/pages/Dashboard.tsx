import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";
import api from "../api/client";

const COLORS = ["#1f4e78", "#2e6da4", "#5b9bd5", "#a9cce3", "#d6eaf8"];

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [topAnalyses, setTopAnalyses] = useState<any[]>([]);

  useEffect(() => {
    api.get("/api/reports/dashboard").then((r) => setStats(r.data)).catch(() => {});
    api.get("/api/reports/all-analyses").then((r) => {
      const rows = (r.data.analyses || [])
        .map((a: any) => ({ name: a.name, count: a.count }))
        .sort((x: any, y: any) => y.count - x.count).slice(0, 6);
      setTopAnalyses(rows);
    }).catch(() => {});
  }, []);

  if (!stats) return <div>Chargement...</div>;

  const pieData = Object.entries(stats.documents_by_type || {})
    .map(([name, value]) => ({ name, value }));

  return (
    <div>
      <h1 className="page-title">Tableau de bord</h1>

      <div className="grid grid-4">
        <div className="card stat"><div className="num">{stats.total_documents}</div>
          <div className="label">Documents</div></div>
        <div className="card stat"><div className="num">{stats.total_analyses}</div>
          <div className="label">Analyses extraites</div></div>
        <div className="card stat"><div className="num" style={{ color: "#dc2626" }}>
          {stats.out_of_range_count}</div><div className="label">Hors normes</div></div>
        <div className="card stat"><div className="num">{stats.out_of_range_percent}%</div>
          <div className="label">Taux hors normes</div></div>
      </div>

      <div className="grid grid-2 mt">
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Types de documents</h3>
          {pieData.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%"
                     outerRadius={90} label>
                  {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip /><Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="muted">Aucun document.</p>}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Analyses les plus frequentes</h3>
          {topAnalyses.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topAnalyses}>
                <XAxis dataKey="name" fontSize={11} /><YAxis allowDecimals={false} />
                <Tooltip /><Bar dataKey="count" fill="#1f4e78" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="muted">Aucune analyse.</p>}
        </div>
      </div>

      <p className="muted mt">Derniere analyse : {stats.last_analysis_date || "—"}</p>
    </div>
  );
}
