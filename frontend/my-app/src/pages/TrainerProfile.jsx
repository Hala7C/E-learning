import { useTrainerProfile } from "../hooks/useTrainerProfile";
import { educationApi, employmentApi, skillApi, achievementApi } from "../api/trainerProfile";
import TrainerProfileForm from "../components/TrainerProfileForm";
import ProfileSectionEditor from "../components/ProfileSectionEditor";

export default function TrainerProfile() {
  const {
    profile, loading, error, canSubmit,
    createProfile, updateProfile, submitProfile,
  } = useTrainerProfile();

  async function handleSaveProfile(fields) {
    if (profile) {
      await updateProfile(fields);
    } else {
      await createProfile(fields);
    }
  }

  async function handleSubmit() {
    if (!window.confirm("Submit your profile for review? You won't be able to edit it while it's pending.")) {
      return;
    }
    await submitProfile();
  }

  if (loading) return <p>Loading your profile...</p>;

  const isReadOnly = profile?.status === "pending" || profile?.status === "approved";

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Trainer Profile</h1>
      </header>

      {error && <p className="error-text">{error}</p>}

      <TrainerProfileForm profile={profile} onSave={handleSaveProfile} />

      {!profile && (
        <p className="empty-state">
          Save your profile above to start adding education, employment, and skills.
        </p>
      )}

      {profile && (
        <>
          {isReadOnly && (
            <p className="status-line">
              Your profile is <strong>{profile.status}</strong> and can't be edited right now.
            </p>
          )}

          <ProfileSectionEditor
            title="Education"
            api={educationApi}
            fields={[
              { name: "institution", label: "Institution" },
              { name: "degree", label: "Degree" },
              { name: "year", label: "Year", type: "number" },
            ]}
            itemLabel={(item) => `${item.degree} — ${item.institution} (${item.year})`}
          />

          <ProfileSectionEditor
            title="Employment"
            api={employmentApi}
            fields={[
              { name: "company", label: "Company" },
              { name: "position", label: "Position" },
              { name: "start_date", label: "Start date", type: "date" },
              { name: "end_date", label: "End date (leave blank if current)", type: "date", required: false },
            ]}
            itemLabel={(item) =>
              `${item.position} at ${item.company} (${item.start_date} — ${item.end_date || "present"})`
            }
          />

          <ProfileSectionEditor
            title="Skills"
            api={skillApi}
            fields={[
              { name: "name", label: "Skill name" },
              { name: "description", label: "Description", required: false },
              {
                name: "proficiency_level", label: "Proficiency (1=Beginner, 2=Intermediate, 3=Advanced)",
                type: "number",
              },
            ]}
            itemLabel={(item) => `${item.name} (level ${item.proficiency_level})`}
          />

          <ProfileSectionEditor
            title="Achievements"
            api={achievementApi}
            fields={[
              { name: "title", label: "Title", required: false },
              { name: "description", label: "Description", required: false },
              { name: "date_achieved", label: "Date", type: "date", required: false },
            ]}
            itemLabel={(item) => item.title || "Untitled achievement"}
          />

          {profile.status === "draft" && (
            <div className="settings-card">
              <h2>Submit for review</h2>
              <p>
                You need at least one entry in Education, Employment, and Skills before
                submitting.
              </p>
              <button onClick={handleSubmit} disabled={!canSubmit}>
                Submit profile
              </button>
              {!canSubmit && (
                <p className="error-text">Add at least one entry to each required section first.</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
