import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { getHotspots, getTrends } from "../lib/api";

/**
 * Community-facing view — no login required, no personal data shown.
 * Displays anonymized, threshold-aggregated case counts only.
 */
export default function CommunityTrends() {
  const [hotspots, setHotspots] = useState([]);
  const [trendData, setTrendData] = useState([]);

  useEffect(() => {
    getHotspots({ hours: 24 }).then((res) => setHotspots(res.data));
    getTrends({ days: 14 }).then((res) => {
      // reshape rows into { day, [symptom_type]: total } for the line chart
      const byDay = {};
      res.data.forEach(({ day, symptom_type, total }) => {
        byDay[day] = byDay[day] || { day };
        byDay[day][symptom_type] = total;
      });
      setTrendData(Object.values(byDay).sort((a, b) => a.day.localeCompare(b.day)));
    });
  }, []);

  const symptomTypes = [...new Set(hotspots.map((h) => h.symptom_type))];

  return (
    <div className="community-trends">
      <h1>Community Health Trends</h1>
      <p className="disclaimer">
        All data shown here is anonymized and aggregated — no individual reports
        are ever displayed, and areas with too few reports to protect privacy
        are omitted automatically.
      </p>

      <section>
        <h2>14-Day Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            {symptomTypes.map((type, i) => (
              <Line key={type} type="monotone" dataKey={type} stroke={`hsl(${i * 70}, 60%, 45%)`} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </section>

      <section>
        <h2>Active Hotspots (last 24h)</h2>
        <ul className="hotspot-list">
          {hotspots.map((h, i) => (
            <li key={i}>
              <strong>{h.symptom_type}</strong> — {h.report_count} reports near{" "}
              {h.latitude?.toFixed(2)}, {h.longitude?.toFixed(2)}
            </li>
          ))}
          {hotspots.length === 0 && <li>No active hotspots reported.</li>}
        </ul>
      </section>
    </div>
  );
}
