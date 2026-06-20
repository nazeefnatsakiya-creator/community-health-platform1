import { useEffect, useState } from "react";
import { logSymptom, listSymptoms } from "../lib/api";

const COMMON_SYMPTOMS = ["Fever", "Cough", "Sore throat", "Fatigue", "Headache", "Nausea"];

export default function SymptomTracker() {
  const [symptoms, setSymptoms] = useState([]);
  const [type, setType] = useState(COMMON_SYMPTOMS[0]);
  const [severity, setSeverity] = useState(3);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const refresh = () => listSymptoms().then((res) => setSymptoms(res.data));

  useEffect(() => {
    refresh();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await logSymptom({ symptom_type: type, severity, notes: notes || null });
      setNotes("");
      await refresh();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card">
      <h2>Symptoms</h2>
      <form onSubmit={handleSubmit} className="card__form">
        <label>
          Symptom
          <select value={type} onChange={(e) => setType(e.target.value)}>
            {COMMON_SYMPTOMS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>

        <label>
          Severity: {severity}/10
          <input
            type="range"
            min="1"
            max="10"
            value={severity}
            onChange={(e) => setSeverity(Number(e.target.value))}
          />
        </label>

        <label>
          Notes (optional)
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Anything else you'd like to record"
          />
        </label>

        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Log symptom"}
        </button>
      </form>

      <ul className="card__history">
        {symptoms.slice(0, 5).map((s) => (
          <li key={s.id}>
            <strong>{s.symptom_type}</strong> — severity {s.severity}/10
            <span className="timestamp">{new Date(s.logged_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
