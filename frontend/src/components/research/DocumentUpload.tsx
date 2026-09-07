"use client";

import { useRef, useState, type FormEvent } from "react";

import { Button, Card } from "@/components/ui";
import { uploadDocument, type UploadDocumentResponse } from "@/lib/api";


const ACCEPTED_FORMATS = ".pdf,.docx,.txt,.md,.markdown,.csv,.xlsx";
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;


export function DocumentUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<UploadDocumentResponse | null>(null);

  function handleFileChange(nextFile: File | null) {
    setError("");
    setResult(null);
    if (nextFile && nextFile.size > MAX_UPLOAD_BYTES) {
      setFile(null);
      setError("Files must be smaller than 10 MB.");
      return;
    }
    setFile(nextFile);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a document before uploading.");
      return;
    }
    setError("");
    setResult(null);
    setIsUploading(true);
    try {
      setResult(await uploadDocument(file));
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Document upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <Card className="mx-auto mt-5 max-w-4xl p-5 sm:p-6">
      <form onSubmit={handleSubmit} aria-labelledby="document-upload-title">
        <div>
          <h3 id="document-upload-title" className="text-base font-semibold text-[var(--text-primary)]">
            Add a research document
          </h3>
          <p id="document-upload-help" className="mt-1 text-sm text-[var(--text-muted)]">
            Upload PDF, DOCX, TXT, Markdown, CSV, or XLSX files up to 10 MB for semantic retrieval.
          </p>
        </div>

        <div className="mt-4">
          <label htmlFor="research-document" className="mb-2 block text-sm font-semibold text-[var(--text-primary)]">
            Document file
          </label>
          <input
            ref={inputRef}
            id="research-document"
            type="file"
            accept={ACCEPTED_FORMATS}
            onChange={(event) => handleFileChange(event.target.files?.[0] ?? null)}
            disabled={isUploading}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "document-upload-error" : "document-upload-help"}
            className="block w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--text-primary)] file:mr-3 file:rounded-[var(--radius-sm)] file:border-0 file:bg-[var(--primary-soft)] file:px-3 file:py-2 file:font-semibold file:text-[var(--primary)]"
          />
        </div>

        {file && <p className="mt-2 text-sm text-[var(--text-secondary)]">Selected: {file.name}</p>}

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <Button type="submit" isLoading={isUploading} disabled={!file}>
            {isUploading ? "Indexing document" : "Upload and index"}
          </Button>
        </div>

        {isUploading && <p role="status" aria-live="polite" className="mt-3 text-sm text-[var(--text-secondary)]">Reading and indexing your document...</p>}
        {error && <p id="document-upload-error" role="alert" className="mt-3 text-sm font-medium text-[var(--danger)]">{error}</p>}
        {result && <p role="status" aria-live="polite" className="mt-3 text-sm font-medium text-[var(--success)]">{result.filename} indexed successfully. {result.chunks} chunks are ready for retrieval.</p>}
      </form>
    </Card>
  );
}