import type { Blog, BlogRequest, Language } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail ?? "Request failed.";
    throw new Error(detail);
  }

  return payload as T;
}

export async function getLanguages(): Promise<Language[]> {
  const response = await fetch(`${API_BASE_URL}/languages`, { cache: "no-store" });
  const payload = await parseResponse<{ languages: Language[] }>(response);
  return payload.languages;
}

export async function getBlogs(): Promise<Blog[]> {
  const response = await fetch(`${API_BASE_URL}/blogs`, { cache: "no-store" });
  return parseResponse<Blog[]>(response);
}

export async function createBlog(payload: BlogRequest): Promise<Blog> {
  const response = await fetch(`${API_BASE_URL}/blogs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return parseResponse<Blog>(response);
}

export async function deleteBlog(blogId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/blogs/${blogId}`, {
    method: "DELETE",
  });
  await parseResponse<{ deleted: boolean }>(response);
}
