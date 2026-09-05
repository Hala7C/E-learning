import { useState, useEffect, useCallback } from "react";
import { courseApi, categoryApi, topicApi, cycleApi } from "../api/courses";
import { formatApiError } from "../utils/errors";

export function useCourseCycles(courseId) {
  const [course, setCourse] = useState(null);
  const [categoryName, setCategoryName] = useState("");
  const [topics, setTopics] = useState([]);
  const [cycles, setCycles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [courseData, topicList, cycleList, categories] = await Promise.all([
        courseApi.get(courseId),
        topicApi.listForCourse(courseId),
        cycleApi.listForCourse(courseId),
        categoryApi.list(),
      ]);
      setCourse(courseData);
      setTopics(topicList);
      // Sort newest-first for display, same as the trainer courses list.
      setCycles([...cycleList].sort((a, b) => b.NumberCycle - a.NumberCycle));
      // Course.category on CourseSerializer is a bare id (PrimaryKeyRelatedField),
      // not a nested object, so the name has to be resolved against the category list.
      const match = categories.find((c) => c.id === courseData.category);
      setCategoryName(match ? match.name : "");
    } catch (err) {
      setError(formatApiError(err, "Couldn't load this course's cycles. Please try again."));
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    load();
  }, [load]);

  const nextCycleNumber = cycles.length
    ? Math.max(...cycles.map((c) => c.NumberCycle)) + 1
    : 1;

  async function createCycle({ startDate, endDate, sessions }) {
    setSaving(true);
    setError(null);
    try {
      await cycleApi.create({
        course: courseId,
        NumberCycle: nextCycleNumber,
        StartDate: startDate,
        EndDate: endDate,
        strategy: "zoom",
        lives_data: sessions.map((s) => ({
          liveSessionMainDataID: s.topicId,
          StartTime: s.start,
          EndTime: s.end,
          price: s.price,
        })),
      });
      await load();
      return true;
    } catch (err) {
      setError(formatApiError(err, "Couldn't create this cycle. Check the schedule and try again."));
      return false;
    } finally {
      setSaving(false);
    }
  }

  return {
    course, categoryName, topics, cycles, nextCycleNumber,
    loading, error, saving, createCycle, refresh: load,
  };
}
