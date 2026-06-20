import { useEffect, useState } from "react";
import { addMedication, listMedications, removeMedication } from "../lib/api";

export default function MedicationList() {
  const [meds, setMeds] = useState([]);
  const [name, setName] = useState("");
  const [dosage, setDosage] = useState("");
  const [schedule, setSchedule] = useState("");
  const [saving, setSaving] = useState(false);

  const refresh = () => listMedications().then((res) => setMeds(res.data));

  useEffect(() => {
    refresh();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await addMedication({ name, dosage: dosage || null, schedule: schedule || null });
      setName("");
      setDosage("");
      setSchedule("");
      await refresh();
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async (id) => {
    await removeMedication(id);
    await refresh();
  };

  return (
    <div className="card">
      <h2>Medications</h2>
      <form onSubmit={handleSubmit} className="card__form">
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Amoxicillin" />
        </label>
        <label>
          Dosage
          <input value={dosage} onChange={(e) => setDosage(e.target.value)} placeholder="e.g. 500mg" />
        </label>
        <label>
          Schedule (times per day, e.g. 08:00,20:00)
          <input value={schedule} onChange={(e) => setSchedule(e.target.value)} placeholder="08:00,20:00" />
        </label>
        <button type="submit" disabled={saving}>
          {saving ? "Adding…" : "Add medication"}
        </button>
      </form>

      <ul className="card__history">
        {meds.map((m) => (
          <li key={m.id}>
            <strong>{m.name}</strong> {m.dosage && `— ${m.dosage}`}
            {m.schedule && <span className="timestamp"> · {m.schedule}</span>}
            <button className="link-button" onClick={() => handleRemove(m.id)}>
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
