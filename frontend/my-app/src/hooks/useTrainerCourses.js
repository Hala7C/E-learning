import { useState, useEffect, useCallback } from "react";
import { courseApi, categoryApi } from "../api/courses";
import { formatApiError } from "../utils/errors";

const PAGE_SIZE = 4; // mirrors backend CustomPagination.page_size

export function useTrainerCourses() {
  const [courses, setCourses] = useState([]);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [ordering, setOrdering] = useState("-created_on");
  const [publishedOnly, setPublishedOnly] = useState(false);
  const [page, setPage] = useState(1);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { ordering, page };
      if (search) params.title = search;
      if (categoryId) params["category__id"] = categoryId;
      if (publishedOnly) params.is_student = "true";
      const { results, total: totalCount } = await courseApi.listMine(params);
      setCourses(results);
      setTotal(totalCount);
    } catch (err) {
      setError(formatApiError(err, "Couldn't load your courses. Please try again."));
    } finally {
      setLoading(false);
    }
  }, [search, categoryId, ordering, publishedOnly, page]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    categoryApi.list().then(setCategories).catch(() => {});
  }, []);

  // Any filter change should reset back to page 1, or a search that
  // narrows the result set could leave the user stranded on an
  // out-of-range page showing nothing.
  useEffect(() => {
    setPage(1);
  }, [search, categoryId, ordering, publishedOnly]);

  async function createCourse(fields) {
    setError(null);
    try {
      await courseApi.create(fields);
      await load();
      return true;
    } catch (err) {
      setError(formatApiError(err, "Couldn't create this course. Please try again."));
      return false;
    }
  }

  async function updateCourse(id, fields) {
    setError(null);
    try {
      await courseApi.update(id, fields);
      await load();
      return true;
    } catch (err) {
      setError(formatApiError(err, "Couldn't save this course. Please try again."));
      return false;
    }
  }

  async function removeCourse(id) {
    setError(null);
    try {
      await courseApi.remove(id);
      await load();
      return true;
    } catch (err) {
      setError(formatApiError(err, "Couldn't delete this course. Please try again."));
      return false;
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return {
    courses, total, totalPages, page, setPage,
    categories, loading, error,
    search, setSearch, categoryId, setCategoryId,
    ordering, setOrdering, publishedOnly, setPublishedOnly,
    createCourse, updateCourse, removeCourse, refresh: load,
  };
}
