import { useState } from "react";
import { useTrainerCourses } from "../hooks/useTrainerCourses";
import CourseCard from "../components/CourseCard";
import CourseForm from "../components/CourseForm";
import "../styles/courses.css";

export default function TrainerCourses() {
  const {
    courses, totalPages, page, setPage, categories,
    loading, error,
    search, setSearch, categoryId, setCategoryId,
    ordering, setOrdering, publishedOnly, setPublishedOnly,
    createCourse, updateCourse, removeCourse,
  } = useTrainerCourses();

  const [adding, setAdding] = useState(false);

  async function handleCreate(fields) {
    const ok = await createCourse(fields);
    if (ok) setAdding(false);
    return ok;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>My courses</h1>
        <button type="button" onClick={() => setAdding((v) => !v)}>
          {adding ? "Cancel" : "Add course"}
        </button>
      </header>

      {error && <p className="error-text">{error}</p>}

      {adding && (
        <div className="settings-card">
          <CourseForm categories={categories} onSave={handleCreate} onCancel={() => setAdding(false)} />
        </div>
      )}

      <div className="settings-card">
        <input
          type="text"
          placeholder="Search by title"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="course-filter-row">
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">All categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
          <select value={ordering} onChange={(e) => setOrdering(e.target.value)}>
            <option value="-created_on">Newest</option>
            <option value="-num_subscribers">Most subscribers</option>
            <option value="-average_rate">Highest rated</option>
          </select>
        </div>
        <label className="course-checkbox-label">
          <input
            type="checkbox"
            checked={publishedOnly}
            onChange={(e) => setPublishedOnly(e.target.checked)}
          />
          Published only
        </label>
      </div>

      {loading ? (
        <p>Loading your courses...</p>
      ) : courses.length === 0 ? (
        <p className="empty-state">No courses match your filters.</p>
      ) : (
        <div className="course-list">
          {courses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              categories={categories}
              onUpdate={updateCourse}
              onDelete={removeCourse}
            />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="course-pagination">
          <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <span>Page {page} of {totalPages}</span>
          <button type="button" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}
