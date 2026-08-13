import { useState, useRef, useEffect } from "react";
import api from "../api/client";

interface Msg { role: "user" | "assistant"; content: string; }

const QUICK = [
  "Que signifie la glycemie ?",
  "Montre mes analyses",
  "C'est quoi le cholesterol LDL ?",
  "A quoi sert la vitamine D ?",
];

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [session, setSession] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput(""); setLoading(true);
    try {
      const r = await api.post("/api/chat/message", { message: text, session_id: session });
      setSession(r.data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: r.data.answer }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Erreur : le service est indisponible." }]);
    } finally { setLoading(false); }
  };

  return (
    <div>
      <h1 className="page-title">Assistant medical</h1>
      <div className="quick">
        {QUICK.map((q) => <button key={q} onClick={() => send(q)}>{q}</button>)}
      </div>
      <div className="card chat-wrap">
        <div className="chat-messages">
          {messages.length === 0 && (
            <p className="muted" style={{ textAlign: "center", marginTop: 40 }}>
              Posez une question sur vos analyses ou un terme medical.
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>{m.content}</div>
          ))}
          {loading && <div className="msg assistant">L'assistant reflechit...</div>}
          <div ref={endRef} />
        </div>
        <div className="chat-input">
          <input value={input} onChange={(e) => setInput(e.target.value)}
            placeholder="Ecrire un message..."
            onKeyDown={(e) => e.key === "Enter" && send(input)} />
          <button onClick={() => send(input)} disabled={loading}>Envoyer</button>
        </div>
      </div>
    </div>
  );
}
