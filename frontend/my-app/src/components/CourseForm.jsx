import { useState } from "react";

export default function CourseForm({ course, categories, onSave, onCancel }) {
  const [form, setForm] = useState({
    title: course?.title || "",
    content: course?.content || "",
    category: course?.category || "",
    status: course?.status || "unpublish",
  });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.title.trim()) {
      setError("Enter a course title.");
      return;
    }
    if (!form.category) {
      setError("Choose a category.");
      return;
    }
    setSaving(true);
    const ok = await onSave(form);
    setSaving(false);
    if (!ok) setError("Couldn't save this course. Please try again.");
  }

  return (
    <form className="inline-form" onSubmit={handleSubmit}>
      {error && <p className="error-text">{error}</p>}
      <label>
        Title
        <input name="title" value={form.title} onChange={handleChange} required />
      </label>
      <label>
        Description <span className="optional-tag">(optional)</span>
        <textarea name="content" rows={3} value={form.content} onChange={handleChange} />
      </label>
      <label>
        Category
        <select name="category" value={form.category} onChange={handleChange}>
          <option value="">Select a category</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>
      </label>
      <label>
        Status
        <select name="status" value={form.status} onChange={handleChange}>
          <option value="unpublish">Draft</option>
          <option value="published">Published</option>
        </select>
      </label>
      <div className="form-actions">
        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : course ? "Save changes" : "Create course"}
        </button>
        <button type="button" className="link-button" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}
