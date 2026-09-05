import { useState } from "react";
import { getTopicTitle, isZoomLinkReady } from "../api/courses";

export default function CycleCard({ cycle, topics }) {
  const [expanded, setExpanded] = useState(false);
  const sessions = cycle.livesessiondetails || [];
  const pendingCount = sessions.filter((s) => !isZoomLinkReady(s)).length;
  const topicById = Object.fromEntries(topics.map((t) => [t.id, t]));

  return (
    <div className="cycle-card">
      <button type="button" className="cycle-card-header" onClick={() => setExpanded((v) => !v)}>
        <div className="cycle-card-title">
          <p>Cycle {cycle.NumberCycle}</p>
          <p className="cycle-card-dates">{cycle.StartDate} – {cycle.EndDate}</p>
        </div>
        <div className="cycle-card-meta">
          <span>{cycle.num_subscribers ?? 0} enrolled</span>
          {pendingCount > 0 && <span className="cycle-badge-pending">{pendingCount} pending</span>}
          <span className={`cycle-chevron ${expanded ? "cycle-chevron-open" : ""}`} aria-hidden="true">▾</span>
        </div>
      </button>

      {expanded && (
        <div className="cycle-session-list">
          {sessions.map((session) => {
            const topic = topicById[session.liveSessionMainDataID];
            const ready = isZoomLinkReady(session);
            return (
              <div key={session.id} className="cycle-session-row">
                <div>
                  <p>{topic ? getTopicTitle(topic) : "Untitled session"}</p>
                  <p className="cycle-session-meta">
                    {new Date(session.StartTime).toLocaleDateString()} · ${session.price}
                  </p>
                </div>
                <span className={ready ? "cycle-badge-ready" : "cycle-badge-pending"}>
                  {ready ? "Link ready" : "Generating"}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
