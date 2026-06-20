import { useEffect, useState } from "react";
import SymptomTracker from "../components/SymptomTracker";
import MoodLog from "../components/MoodLog";
import MedicationList from "../components/MedicationList";
import AlertBanner from "../components/AlertBanner";

/**
 * Personal dashboard: the user's private home base. Large touch targets and
 * high-contrast text by default so it works well for older adults; a
 * "comfort mode" toggle bumps font size further for low-vision users.
 */
export default function Dashboard() {
  const [comfortMode, setComfortMode] = useState(false);

  return (
    <div className={`dashboard ${comfortMode ? "comfort-mode" : ""}`}>
      <header className="dashboard__header">
        <h1>Your Health Dashboard</h1>
        <label className="comfort-toggle">
          <input
            type="checkbox"
            checked={comfortMode}
            onChange={(e) => setComfortMode(e.target.checked)}
          />
          Large text mode
        </label>
      </header>

      <AlertBanner />

      <section className="dashboard__grid">
        <SymptomTracker />
        <MoodLog />
        <MedicationList />
      </section>
    </div>
  );
}
