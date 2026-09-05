import { useState } from "react";
import { getTopicTitle } from "../api/courses";

function emptySessionState(topics) {
  return Object.fromEntries(topics.map((t) => [t.id, { start: "", end: "", price: "" }]));
}

export default function AddCycleForm({ topics, nextCycleNumber, saving, onSubmit, onCancel }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [sessions, setSessions] = useState(() => emptySessionState(topics));
  const [error, setError] = useState(null);

  function updateSession(topicId, field, value) {
    setSessions((prev) => ({ ...prev, [topicId]: { ...prev[topicId], [field]: value } }));
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!startDate || !endDate) {
      setError("Enter a start and end date for the cycle.");
      return;
    }
    if (new Date(endDate) <= new Date(startDate)) {
      setError("Cycle end date must be after the start date.");
      return;
    }

    const payloadSessions = [];
    for (const topic of topics) {
      const s = sessions[topic.id];
      const title = getTopicTitle(topic);
      if (!s.start || !s.end || s.price === "") {
        setError(`Fill in every field for ${title}.`);
        return;
      }
      if (new Date(s.end) <= new Date(s.start)) {
        setError(`Session end time must be after start time for ${title}.`);
        return;
      }
      if (Number(s.price) < 0) {
        setError(`Price can't be negative for ${title}.`);
        return;
      }
      payloadSessions.push({ topicId: topic.id, start: s.start, end: s.end, price: Number(s.price) });
    }

    const ok = await onSubmit({ startDate, endDate, sessions: payloadSessions });
    if (ok) {
      setStartDate("");
      setEndDate("");
      setSessions(emptySessionState(topics));
    }
  }

  return (
    <form className="settings-card" onSubmit={handleSubmit}>
      <h2>Cycle {nextCycleNumber}</h2>

      <div className="course-filter-row">
        <label>
          Start date
          <input type="date" value={startDate} onChange={(e) => { setStartDate(e.target.value); setError(null); }} />
        </label>
        <label>
          End date
          <input type="date" value={endDate} onChange={(e) => { setEndDate(e.target.value); setError(null); }} />
        </label>
      </div>

      {topics.map((topic) => (
        <div key={topic.id} className="cycle-session-block">
          <p className="cycle-session-title">{getTopicTitle(topic)}</p>
          <div className="course-filter-row">
            <label>
              Start
              <input
                type="datetime-local"
                value={sessions[topic.id]?.start || ""}
                onChange={(e) => updateSession(topic.id, "start", e.target.value)}
              />
            </label>
            <label>
              End
              <input
                type="datetime-local"
                value={sessions[topic.id]?.end || ""}
                onChange={(e) => updateSession(topic.id, "end", e.target.value)}
              />
            </label>
          </div>
          <label>
            Price
            <input
              type="number"
              min="0"
              step="1"
              value={sessions[topic.id]?.price ?? ""}
              onChange={(e) => updateSession(topic.id, "price", e.target.value)}
            />
          </label>
        </div>
      ))}

      {error && <p className="error-text">{error}</p>}

      <div className="form-actions">
        <button type="submit" disabled={saving}>{saving ? "Creating..." : "Create cycle"}</button>
        <button type="button" className="link-button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}
