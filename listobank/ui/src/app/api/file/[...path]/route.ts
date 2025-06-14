import { promises as fs } from 'fs';
import path from 'path';
import { lookup } from 'mime-types';
import { NextResponse } from 'next/server';

// App Router route handler: /app/api/files/[...path]/route.js
export async function GET(request: Request, { params }: Promise<{
  params: { path?: string[] };
}>) {
  console.log("Hello")
  const pathSegments = (await params).path || [];
  const dataDir = path.join(process.cwd(), '..', 'data');

  // Construct the requested file's relative path
  const relativePath = Array.isArray(pathSegments) ? pathSegments.join(path.sep) : '';
  const filePath = path.join(dataDir, relativePath);

  console.log('Requested file path:', filePath);
  console.log('Data directory:', dataDir);  
  console.log('Relative path:', relativePath);

  // Prevent path traversal: ensure filePath is inside dataDir
  if (!filePath.startsWith(dataDir)) {
    return NextResponse.json({ error: 'Invalid file path' }, { status: 400 });
  }

  try {
    // Read the file as a Buffer
    const fileBuffer = await fs.readFile(filePath);

    // Convert Node Buffer to Uint8Array for Response compatibility
    const fileArray = new Uint8Array(fileBuffer);

    // Determine MIME type based on file extension
    const mimeType = lookup(path.extname(filePath)) || 'application/octet-stream';

    // Return file in response
    return new Response(fileArray, {
      status: 200,
      headers: { 'Content-Type': mimeType },
    });
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }
    console.error('File read error:', err);
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
