import api from "./client";

// Base profile - the draft/editable profile itself (name, bio, picture, etc.)
export const trainerProfileApi = {
  get: () => api.get("/api/trainer/draftProfile/me/"),
  // profile_picture may be a File, so this always sends multipart -
  // FormData works fine for text fields too, and lets axios set the
  // correct boundary automatically (same pattern as receipt upload
  // in the expense tracker project - don't set Content-Type manually).
  create: (fields) => api.post("/api/trainer/draftProfile/", toFormData(fields)),
  update: (id, fields) => api.put(`/api/trainer/draftProfile/${id}/`, toFormData(fields)),
  submit: (id) => api.put(`/api/trainer/submitDraftProfile/${id}/`, {}),
};

// The four "section" endpoints all share the same shape - list responses
// come back wrapped as { data: [...] }, create/update return the plain
// object, delete returns 204. One generic factory instead of repeating
// this four times.
function makeSectionApi(endpoint) {
  return {
    list: () => api.get(`/api/trainer/${endpoint}/`).then((res) => res.data.data),
    create: (fields) => api.post(`/api/trainer/${endpoint}/`, fields),
    update: (id, fields) => api.put(`/api/trainer/${endpoint}/${id}/`, fields),
    remove: (id) => api.delete(`/api/trainer/${endpoint}/${id}/`),
  };
}

export const educationApi = makeSectionApi("education");
export const employmentApi = makeSectionApi("employment");
export const skillApi = makeSectionApi("skill");
export const achievementApi = makeSectionApi("achievement");

function toFormData(fields) {
  const formData = new FormData();
  Object.entries(fields).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      formData.append(key, value);
    }
  });
  return formData;
}
