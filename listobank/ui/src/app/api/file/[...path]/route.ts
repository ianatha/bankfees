import path from 'path';
import { lookup } from 'mime-types';
import { NextResponse } from 'next/server';
import Database from 'better-sqlite3';

// App Router route handler: /app/api/files/[...path]/route.js
export async function GET(request: Request, { params }: { params: { path?: string[] } }) {
  const pathSegments = params.path || [];
  const relativePath = Array.isArray(pathSegments) ? pathSegments.join(path.sep) : '';

  if (relativePath.includes('..')) {
    return NextResponse.json({ error: 'Invalid file path' }, { status: 400 });
  }

  const dbPath = path.join(process.cwd(), 'documents.sqlite');

  try {
    const db = new Database(dbPath, { readonly: true });
    const row = db.prepare('SELECT pdf FROM documents WHERE path = ?').get(relativePath);
    db.close();

    if (!row) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    const fileBuffer: Buffer = row.pdf;
    const mimeType = lookup(path.extname(relativePath)) || 'application/pdf';

    return new Response(fileBuffer, {
      status: 200,
      headers: { 'Content-Type': mimeType },
    });
  } catch (err) {
    console.error('Database error:', err);
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
