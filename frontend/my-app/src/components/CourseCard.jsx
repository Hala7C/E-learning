import { useState } from "react";
import { Link } from "react-router-dom";
import CourseForm from "./CourseForm";

function statusInfo(course) {
  if (course.is_blocked) return { label: "Blocked", className: "course-badge-blocked" };
  if (course.status === "published") return { label: "Published", className: "course-badge-published" };
  return { label: "Draft", className: "course-badge-draft" };
}

export default function CourseCard({ course, categories, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const badge = statusInfo(course);
  // course.category is a bare id (PrimaryKeyRelatedField) - resolve it
  // against the categories list rather than assuming a nested object.
  const category = categories.find((cat) => cat.id === course.category);

  async function handleSave(fields) {
    const ok = await onUpdate(course.id, fields);
    if (ok) setEditing(false);
    return ok;
  }

  async function handleDelete() {
    if (!window.confirm(`Delete "${course.title}"? This can't be undone.`)) return;
    await onDelete(course.id);
  }

  if (editing) {
    return (
      <div className="course-card">
        <CourseForm
          course={course}
          categories={categories}
          onSave={handleSave}
          onCancel={() => setEditing(false)}
        />
      </div>
    );
  }

  return (
    <div className="course-card">
      <div className="course-card-header">
        <div className="course-card-title">
          <p>{course.title}</p>
          <p className="course-card-category">{category?.name || ""}</p>
        </div>
        <span className={`course-badge ${badge.className}`}>{badge.label}</span>
      </div>

      <div className="course-card-stats">
        <span>{course.num_subscribers ?? 0} subscribers</span>
        <span>{course.average_rate ? course.average_rate.toFixed(1) : "No ratings"}</span>
      </div>

      <div className="course-card-actions">
        <button type="button" onClick={() => setEditing(true)}>Edit</button>
        <Link to={`/trainer/courses/${course.id}/cycles`}>Manage cycles</Link>
        <button type="button" className="danger" onClick={handleDelete}>Delete</button>
      </div>
    </div>
  );
}
