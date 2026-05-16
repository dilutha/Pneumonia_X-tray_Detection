import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    // Forward the multipart form data to FastAPI
    const formData = await request.formData();
    
    const backendResponse = await fetch(`${BACKEND_URL}/api/v1/predict`, {
      method: "POST",
      body: formData,
    });

    if (!backendResponse.ok) {
      const error = await backendResponse.json();
      return NextResponse.json(error, { status: backendResponse.status });
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("Predict API proxy error:", error);
    return NextResponse.json(
      { error: "Failed to connect to analysis service" },
      { status: 503 },
    );
  }
}
