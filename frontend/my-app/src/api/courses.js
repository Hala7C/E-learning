import api from "./client";

// Course and Cycle list endpoints wrap results as { data: { total_count, results } }.
// LiveSessionMainDataSection falls back to DRF's default paginator:
// { count, next, previous, results }. Normalizing here means every hook
// downstream can treat "a list response" as one shape.
function unwrapListResponse(data) {
  if (data?.data?.results) {
    return { results: data.data.results, total: data.data.total_count };
  }
  if (data?.results) {
    return { results: data.results, total: data.count };
  }
  const list = Array.isArray(data) ? data : [];
  return { results: list, total: list.length };
}

export const courseApi = {
  listMine: async (params) => {
    const { data } = await api.get("/api/trainer/course/getTrainerCourse/", { params });
    return unwrapListResponse(data);
  },
  get: (id) => api.get(`/api/trainer/course/${id}/`).then((res) => res.data),
  create: (fields) => api.post("/api/trainer/course/", fields).then((res) => res.data),
  update: (id, fields) => api.put(`/api/trainer/course/${id}/`, fields).then((res) => res.data),
  remove: (id) => api.delete(`/api/trainer/course/${id}/`),
};

export const categoryApi = {
  list: () => api.get("/api/trainer/category/").then((res) => res.data),
};

export const topicApi = {
  // page_size=100 sidesteps CustomPagination's default page_size=4 -
  // without it, courses with more than 4 topics would silently lose some
  // from this list.
  listForCourse: async (courseId) => {
    const { data } = await api.get("/api/trainer/live_session/", {
      params: { course: courseId, page_size: 100 },
    });
    return unwrapListResponse(data).results;
  },
};

export const cycleApi = {
  listForCourse: async (courseId) => {
    const { data } = await api.get("/api/trainer/cycle/", {
      params: { course: courseId, page_size: 100 },
    });
    return unwrapListResponse(data).results;
  },
  create: (fields) => api.post("/api/trainer/cycle/", fields).then((res) => res.data),
};

// LiveSessionMainDataSectionSerializer returns translations as
// { en: { title, description }, ar: { ... } } via parler_rest - there's
// no flat "title" field to read directly.
export function getTopicTitle(topic) {
  const lang = localStorage.getItem("lang") || "en";
  return topic?.translations?.[lang]?.title || topic?.translations?.en?.title || "Untitled topic";
}

// The backend sets ZoomMeetingURL to this literal placeholder when a
// cycle is created, then overwrites it once the async Celery task
// finishes creating the real meeting. There's no dedicated status field,
// so "still the placeholder" is the only signal available today.
const ZOOM_PLACEHOLDER_URL = "http://zoom.com";
export function isZoomLinkReady(session) {
  return Boolean(session.ZoomMeetingURL) && session.ZoomMeetingURL !== ZOOM_PLACEHOLDER_URL;
}
