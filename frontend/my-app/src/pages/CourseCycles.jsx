import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useCourseCycles } from "../hooks/useCourseCycles";
import { getTopicTitle } from "../api/courses";
import CycleCard from "../components/CycleCard";
import AddCycleForm from "../components/AddCycleForm";
import "../styles/courses.css";

export default function CourseCycles() {
  const { courseId } = useParams();
  const {
    course, categoryName, topics, cycles, nextCycleNumber,
    loading, error, saving, createCycle,
  } = useCourseCycles(courseId);

  const [addingCycle, setAddingCycle] = useState(false);

  async function handleCreate(payload) {
    const ok = await createCycle(payload);
    if (ok) setAddingCycle(false);
    return ok;
  }

  if (loading) return <p className="dashboard">Loading...</p>;

  return (
    <div className="dashboard">
      <Link to="/trainer/courses" className="cycle-back-link">&larr; My courses</Link>

      <header className="dashboard-header">
        <div>
          <h1>{course?.title}</h1>
          <p className="course-card-category">{categoryName}</p>
        </div>
      </header>

      {error && <p className="error-text">{error}</p>}

      <div className="settings-card">
        <h2>Session topics</h2>
        {topics.length === 0 ? (
          <p className="empty-state">Add session topics to this course before scheduling a cycle.</p>
        ) : (
          <div className="topic-chip-row">
            {topics.map((topic) => (
              <span key={topic.id} className="topic-chip">{getTopicTitle(topic)}</span>
            ))}
          </div>
        )}
      </div>

      <div className="dashboard-header">
        <h2>Cycles</h2>
        {topics.length > 0 && (
          <button type="button" onClick={() => setAddingCycle((v) => !v)}>
            {addingCycle ? "Cancel" : "Add cycle"}
          </button>
        )}
      </div>

      {addingCycle && (
        <AddCycleForm
          topics={topics}
          nextCycleNumber={nextCycleNumber}
          saving={saving}
          onSubmit={handleCreate}
          onCancel={() => setAddingCycle(false)}
        />
      )}

      {cycles.length === 0 ? (
        <p className="empty-state">No cycles scheduled yet.</p>
      ) : (
        <div className="course-list">
          {cycles.map((cycle) => (
            <CycleCard key={cycle.id} cycle={cycle} topics={topics} />
          ))}
        </div>
      )}
    </div>
  );
}
