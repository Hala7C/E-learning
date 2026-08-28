import { useState, useEffect, useCallback } from "react";
import {
  trainerProfileApi, educationApi, employmentApi, skillApi, achievementApi,
} from "../api/trainerProfile";
import { formatApiError } from "../utils/errors";

export function useTrainerProfile() {
  const [profile, setProfile] = useState(null); // null = no profile yet
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await trainerProfileApi.get();
      setProfile(data);
    } catch (err) {
      if (err.response?.status === 404) {
        // Genuinely no profile yet - not an error state, just "not created".
        setProfile(null);
      } else {
        setError("Couldn't load your profile. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function createProfile(fields) {
    setError(null);
    try {
      await trainerProfileApi.create(fields);
      await load(); // re-fetch to get the full nested shape with sections
      return true;
    } catch (err) {
      setError(formatDetailError(err));
      return false;
    }
  }

  async function updateProfile(fields) {
    setError(null);
    try {
      await trainerProfileApi.update(profile.id, fields);
      await load();
      return true;
    } catch (err) {
      setError(formatDetailError(err));
      return false;
    }
  }

  async function submitProfile() {
    setError(null);
    try {
      await trainerProfileApi.submit(profile.id);
      await load();
      return true;
    } catch (err) {
      setError(formatDetailError(err));
      return false;
    }
  }

  // Requirements the backend enforces on submit - mirrored here so the
  // UI can disable the button proactively instead of letting the user
  // hit submit and get a validation error back.
  const canSubmit =
    profile &&
    profile.status === "draft" &&
    (profile.education?.length || 0) > 0 &&
    (profile.skills?.length || 0) > 0 &&
    (profile.employments?.length || 0) > 0;

  return {
    profile, loading, error, canSubmit,
    createProfile, updateProfile, submitProfile, refresh: load,
  };
}

// BUG FIX: this previously called an undefined `formatError`, which threw a
// ReferenceError on every failed create/update/submit instead of showing
// the user a message. This backend's convention for field-level errors is
// { error: "..." }; fall back to the generic formatter otherwise.
function formatDetailError(err) {
  const data = err.response?.data;
  if (data?.error) return data.error;
  return formatApiError(err);
}
