import { useState, useEffect } from "react";

export default function TrainerProfileForm({ profile, onSave }) {
  const [form, setForm] = useState({ gender: "", birthday: "", bio: "", first_name: "", last_name: "" });
  const [pictureFile, setPictureFile] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (profile) {
      setForm({
        gender: profile.gender || "",
        birthday: profile.birthday || "",
        bio: profile.bio || "",
        first_name: profile.first_name || "",
        last_name: profile.last_name || "",
      });
    }
  }, [profile]);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    const fields = { ...form };
    if (pictureFile) fields.profile_picture = pictureFile;
    await onSave(fields);
    setSaving(false);
  }

  return (
    <form className="settings-card" onSubmit={handleSubmit}>
      <h2>Profile</h2>

      {profile?.profile_picture && (
        <img src={profile.profile_picture} alt="Profile" className="profile-picture-preview" />
      )}
      <label>
        Profile picture
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setPictureFile(e.target.files[0])}
        />
      </label>

      <label>
        Gender
        <select name="gender" value={form.gender} onChange={handleChange}>
          <option value="">Select...</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </label>

      <label>
        Birthday
        <input type="date" name="birthday" value={form.birthday} onChange={handleChange} />
      </label>

      <label>
        Bio
        <textarea name="bio" rows={4} value={form.bio} onChange={handleChange} />
      </label>

      <label>
        First Name
        <input type="text" name="first_name" value={form.first_name} onChange={handleChange} />
      </label>

      <label>
        Last Name
        <input type="text" name="last_name" value={form.last_name} onChange={handleChange} />
      </label>

      <button type="submit" disabled={saving}>
        {saving ? "Saving..." : "Save profile"}
      </button>

      {profile?.status && (
        <p className="status-line">
          Status: <span className={`status-tag status-${profile.status}`}>{profile.status}</span>
        </p>
      )}
    </form>
  );
}
