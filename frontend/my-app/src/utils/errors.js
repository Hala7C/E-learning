// Turns any axios error into a safe, displayable string. Handles three
// real cases we've hit:
//   1. DRF validation errors - { field: ["message"] } -> flattened text
//   2. A plain string error body
//   3. A raw HTML page (Django's DEBUG=True error page on a 500) - this
//      must NEVER be shown as-is. Object.values() on a string splits it
//      into individual characters, which is what produced the garbled
//      "spaced out HTML" text on screen - this function catches that
//      case explicitly before it can happen.
export function formatApiError(err, fallback = "Something went wrong. Please try again.") {
  if (!err.response) {
    return "Couldn't reach the server. Check your connection and try again.";
  }

  const data = err.response.data;

  if (!data) return fallback;

  if (typeof data === "string") {
    const looksLikeHtml = data.trim().startsWith("<");
    return looksLikeHtml ? fallback : data;
  }

  if (typeof data === "object") {
    try {
      return Object.values(data).flat().join(" ");
    } catch {
      return fallback;
    }
  }

  return fallback;
}
