"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { createBlog, deleteBlog, getBlogs, getLanguages } from "./api";
import type { Blog, BlogRequest, Language } from "./types";

const fallbackLanguages: Language[] = [
  { code: "english", name: "English" },
  { code: "french", name: "French" },
  { code: "hindi", name: "Hindi" },
  { code: "spanish", name: "Spanish" },
  { code: "german", name: "German" },
  { code: "telugu", name: "Telugu" },
];

const tones = ["professional", "technical", "beginner-friendly", "conversational", "executive"];
const lengths = ["short", "medium", "long"];

export default function Home() {
  const [languages, setLanguages] = useState<Language[]>(fallbackLanguages);
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [selectedBlog, setSelectedBlog] = useState<Blog | null>(null);
  const [activeTab, setActiveTab] = useState<"blog" | "research" | "history">("blog");
  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error" | "warning"; text: string } | null>(null);
  const [form, setForm] = useState<BlogRequest>({
    topic: "Agentic AI in software engineering",
    language: "English",
    audience: "software engineers",
    tone: "professional",
    length: "short",
  });

  useEffect(() => {
    getLanguages()
      .then(setLanguages)
      .catch(() =>
        setMessage({
          type: "warning",
          text: "Could not load supported languages from the API. Using local defaults.",
        }),
      );
    refreshHistory();
  }, []);

  async function refreshHistory() {
    try {
      const nextBlogs = await getBlogs();
      setBlogs(nextBlogs);
    } catch {
      setMessage({ type: "warning", text: "Could not load blog history. Make sure the API is running." });
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsGenerating(true);
    setMessage(null);
    try {
      const blog = await createBlog(form);
      setSelectedBlog(blog);
      setActiveTab("blog");
      setMessage({ type: "success", text: "Blog generated." });
      await refreshHistory();
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Blog generation failed.",
      });
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleDelete(blogId: number) {
    try {
      await deleteBlog(blogId);
      if (selectedBlog?.id === blogId) {
        setSelectedBlog(null);
      }
      await refreshHistory();
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Could not delete blog.",
      });
    }
  }

  function handlePreview(blog: Blog) {
    setSelectedBlog(blog);
    setActiveTab("blog");
    setMessage(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const markdownDownload = useMemo(() => {
    if (!selectedBlog) {
      return "";
    }

    return `# ${selectedBlog.title}\n\n${selectedBlog.content}`;
  }, [selectedBlog]);

  return (
    <main className="shell">
      <aside className="sidebar">
        <h2>Generation Settings</h2>
        <form onSubmit={handleSubmit} className="form">
          <label>
            Topic
            <input
              value={form.topic}
              onChange={(event) => setForm({ ...form, topic: event.target.value })}
              minLength={3}
              required
            />
          </label>

          <label>
            Language
            <select
              value={form.language}
              onChange={(event) => setForm({ ...form, language: event.target.value })}
            >
              {languages.map((language) => (
                <option key={language.code} value={language.name}>
                  {language.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Audience
            <input
              value={form.audience}
              onChange={(event) => setForm({ ...form, audience: event.target.value })}
            />
          </label>

          <label>
            Tone
            <select value={form.tone} onChange={(event) => setForm({ ...form, tone: event.target.value })}>
              {tones.map((tone) => (
                <option key={tone} value={tone}>
                  {tone}
                </option>
              ))}
            </select>
          </label>

          <label>
            Length
            <select value={form.length} onChange={(event) => setForm({ ...form, length: event.target.value })}>
              {lengths.map((length) => (
                <option key={length} value={length}>
                  {length}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" disabled={isGenerating}>
            {isGenerating ? "Generating..." : "Generate Blog"}
          </button>
        </form>
      </aside>

      <section className="content">
        <header className="header">
          <h1>Agentic Blog Generator</h1>
          <p>Web-grounded multi-agent blog generation with source tracking.</p>
        </header>

        {message ? <div className={`alert ${message.type}`}>{message.text}</div> : null}

        <nav className="tabs" aria-label="Blog sections">
          <button className={activeTab === "blog" ? "active" : ""} onClick={() => setActiveTab("blog")}>
            Blog
          </button>
          <button className={activeTab === "research" ? "active" : ""} onClick={() => setActiveTab("research")}>
            Research & SEO
          </button>
          <button className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")}>
            History
          </button>
        </nav>

        {activeTab === "blog" ? (
          <BlogPanel blog={selectedBlog} markdownDownload={markdownDownload} />
        ) : null}
        {activeTab === "research" ? <ResearchPanel blog={selectedBlog} /> : null}
        {activeTab === "history" ? (
          <HistoryPanel blogs={blogs} onSelect={handlePreview} onDelete={handleDelete} />
        ) : null}
      </section>
    </main>
  );
}

function BlogPanel({ blog, markdownDownload }: { blog: Blog | null; markdownDownload: string }) {
  if (!blog) {
    return <div className="empty">Generate a blog from the sidebar to preview it here.</div>;
  }

  return (
    <article className="blog">
      <div className="meta">
        Blog ID: {blog.id} | Status: {blog.status}
      </div>
      <h2>{blog.title}</h2>
      <MarkdownView content={blog.content} />
      <a
        className="download"
        href={`data:text/markdown;charset=utf-8,${encodeURIComponent(markdownDownload)}`}
        download={`${String(blog.seo?.slug ?? "blog-post")}.md`}
      >
        Download Markdown
      </a>
    </article>
  );
}

function ResearchPanel({ blog }: { blog: Blog | null }) {
  if (!blog) {
    return <div className="empty">Research, sources, editor notes, and SEO metadata appear after generation.</div>;
  }

  return (
    <div className="details">
      <section>
        <h3>Research Notes</h3>
        <MarkdownView content={blog.research_notes || "No research notes saved."} />
      </section>
      <section>
        <h3>Outline</h3>
        <MarkdownView content={blog.outline || "No outline saved."} />
      </section>
      <section>
        <h3>Editor Notes</h3>
        <p>{blog.editor_notes || "No editor notes saved."}</p>
      </section>
      <section>
        <h3>Sources</h3>
        {blog.retrieval_warning ? <div className="alert warning">{blog.retrieval_warning}</div> : null}
        {blog.sources.length ? (
          <ul className="sources">
            {blog.sources.map((source, index) => (
              <li key={`${source.url}-${index}`}>
                <a href={source.url} target="_blank" rel="noreferrer">
                  {source.title || source.url}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p>No web sources were stored for this blog.</p>
        )}
      </section>
      <section>
        <h3>SEO</h3>
        <pre>{JSON.stringify(blog.seo, null, 2)}</pre>
      </section>
    </div>
  );
}

function HistoryPanel({
  blogs,
  onSelect,
  onDelete,
}: {
  blogs: Blog[];
  onSelect: (blog: Blog) => void;
  onDelete: (blogId: number) => void;
}) {
  if (!blogs.length) {
    return <div className="empty">No blogs saved yet.</div>;
  }

  return (
    <div className="history">
      {blogs.map((blog) => (
        <section key={blog.id} className="historyItem">
          <div>
            <h3>{blog.title}</h3>
            <p>
              ID {blog.id} | {blog.topic} | {new Date(blog.created_at).toLocaleString()}
            </p>
          </div>
          <div className="actions">
            <button type="button" onClick={() => onSelect(blog)}>
              Preview
            </button>
            <button type="button" className="secondary" onClick={() => onDelete(blog.id)}>
              Delete
            </button>
          </div>
        </section>
      ))}
    </div>
  );
}

function MarkdownView({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="markdown">
      {lines.map((line, index) => {
        if (line.startsWith("### ")) {
          return <h4 key={index}>{line.replace("### ", "")}</h4>;
        }
        if (line.startsWith("## ")) {
          return <h3 key={index}>{line.replace("## ", "")}</h3>;
        }
        if (line.startsWith("- ")) {
          return <li key={index}>{line.replace("- ", "")}</li>;
        }
        if (!line.trim()) {
          return <br key={index} />;
        }
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}
