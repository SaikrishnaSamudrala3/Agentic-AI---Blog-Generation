export type Language = {
  code: string;
  name: string;
};

export type BlogRequest = {
  topic: string;
  language: string;
  audience: string;
  tone: string;
  length: string;
};

export type Blog = {
  id: number;
  topic: string;
  language: string | null;
  title: string;
  content: string;
  research_notes?: string | null;
  outline?: string | null;
  editor_notes?: string | null;
  sources: Array<{ title?: string; url?: string }>;
  retrieval_warning?: string | null;
  seo: Record<string, unknown>;
  tone?: string | null;
  audience?: string | null;
  length?: string | null;
  status: string;
  created_at: string;
};
