/**
 * One place for every fetch call to the FastAPI backend. Nothing else in
 * the app should call fetch() directly against the backend -- if the
 * API's shape ever changes, this is the only file that needs updating.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(
      body.detail || `Request failed with status ${res.status}`,
      res.status
    );
  }
  return res.json();
}

export async function login(
  username: string,
  password: string
): Promise<{ access_token: string; token_type: string }> {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return handleResponse(res);
}

export async function signup(
  username: string,
  password: string
): Promise<{ message: string }> {
  const res = await fetch(`${API_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return handleResponse(res);
}

export async function getTopics(): Promise<{ topics: string[] }> {
  const res = await fetch(`${API_URL}/topics`);
  return handleResponse(res);
}

export async function askQuestion(
  topic: string,
  query: string,
  token: string
): Promise<{
  answer: string;
  sources: { filename: string; page_number: number }[];
}> {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ topic, query }),
  });
  return handleResponse(res);
}

export async function uploadDocument(
  topic: string,
  file: File,
  token: string
): Promise<{ message: string; topic: string; chunks_inserted: number }> {
  const formData = new FormData();
  formData.append("topic", topic);
  formData.append("file", file);

  // No Content-Type header here on purpose -- the browser sets the
  // multipart/form-data boundary itself when the body is a FormData.
  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  return handleResponse(res);
}
