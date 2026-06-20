import { useEffect, useState } from "react";
import { logMood, listMoodLogs } from "../lib/api";

const FACES = ["😞", "🙁", "😐", "🙂", "😄"];

export default function MoodLog() {
  const [logs, setLogs] = useState([]);
  const [score, setScore] = useState(3);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const refresh = () => listMoodLogs().then((res) => setLogs(res.data));

  useEffect(() => {
    refresh();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await logMood({ mood_score: score, notes: notes || null });
      setNotes("");
      await refresh();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card">
      <h2>Mental Health Check-in</h2>
      <form onSubmit={handleSubmit} className="card__form">
        <div className="mood-picker" role="radiogroup" aria-label="Mood">
          {FACES.map((face, i) => (
            <button
              key={i}
              type="button"
              className={score === i + 1 ? "mood-picker__selected" : ""}
              onClick={() => setScore(i + 1)}
              aria-pressed={score === i + 1}
              aria-label={`Mood level ${i + 1} of 5`}
            >
              {face}
            </button>
          ))}
        </div>

        <label>
          Notes (private, only visible to you)
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="How are you really doing today?"
          />
        </label>

        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save check-in"}
        </button>
      </form>

      <ul className="card__history">
        {logs.slice(0, 5).map((l) => (
          <li key={l.id}>
            {FACES[l.mood_score - 1]}
            <span className="timestamp">{new Date(l.logged_at).toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
