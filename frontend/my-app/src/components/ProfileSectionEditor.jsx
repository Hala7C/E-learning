import { useState, useEffect } from "react";
import { formatApiError } from "../utils/errors";

// One configurable component instead of four copies - Education,
// Employment, Skill, and Achievement all share the exact same
// list/create/update/delete shape on the backend, they just differ in
// which fields they collect. Passing that shape in as config means a
// bug fix or styling change here fixes all four sections at once.
export default function ProfileSectionEditor({ title, api, fields, itemLabel }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null); // null = not editing, "new" = adding
  const [form, setForm] = useState({});

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await api.list();
      setItems(data);
    } catch {
      setError(`Couldn't load ${title.toLowerCase()}.`);
    } finally {
      setLoading(false);
    }
  }

  function startAdd() {
    setForm(Object.fromEntries(fields.map((f) => [f.name, ""])));
    setEditingId("new");
  }

  function startEdit(item) {
    setForm(Object.fromEntries(fields.map((f) => [f.name, item[f.name] ?? ""])));
    setEditingId(item.id);
  }

  function cancelEdit() {
    setEditingId(null);
    setForm({});
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    // Optional fields left blank come through as "" - DRF's DateField
    // (and other typed fields) reject an empty string outright rather
    // than treating it as "not provided", so we drop empty values here
    // instead of sending them as-is.
    const payload = Object.fromEntries(
      Object.entries(form).filter(([, value]) => value !== "")
    );
    try {
      if (editingId === "new") {
        await api.create(payload);
      } else {
        await api.update(editingId, payload);
      }
      cancelEdit();
      await load();
    } catch (err) {
      setError(formatApiError(err, "Couldn't save. Please try again."));
    }
  }

  async function handleDelete(id) {
    if (!window.confirm(`Remove this ${title.toLowerCase()} entry?`)) return;
    try {
      await api.remove(id);
      await load();
    } catch (err) {
      setError(formatApiError(err, "Couldn't delete. Please try again."));
    }
  }

  return (
    <div className="settings-card">
      <div className="section-header">
        <h2>{title}</h2>
        {editingId === null && (
          <button className="link-button" onClick={startAdd}>+ Add</button>
        )}
      </div>

      {error && <p className="error-text">{error}</p>}
      {loading ? (
        <p>Loading...</p>
      ) : items.length === 0 && editingId === null ? (
        <p className="empty-state">No {title.toLowerCase()} added yet.</p>
      ) : (
        <ul className="section-list">
          {items.map((item) => (
            <li key={item.id}>
              <span>{itemLabel(item)}</span>
              <span>
                <button className="link-button" onClick={() => startEdit(item)}>Edit</button>{" "}
                <button className="link-button danger" onClick={() => handleDelete(item.id)}>Delete</button>
              </span>
            </li>
          ))}
        </ul>
      )}

      {editingId !== null && (
        <form onSubmit={handleSubmit} className="inline-form">
          {fields.map((f) => (
            <label key={f.name}>
              {f.label}
              <input
                name={f.name}
                type={f.type || "text"}
                value={form[f.name] ?? ""}
                onChange={handleChange}
                required={f.required !== false}
              />
            </label>
          ))}
          <div className="form-actions">
            <button type="submit">{editingId === "new" ? "Add" : "Save"}</button>
            <button type="button" className="link-button" onClick={cancelEdit}>Cancel</button>
          </div>
        </form>
      )}
    </div>
  );
}
