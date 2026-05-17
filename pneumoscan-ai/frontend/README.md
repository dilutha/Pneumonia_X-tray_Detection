# PneumoScan AI Frontend

Next.js App Router frontend for the PneumoScan AI DenseNet121 transfer learning pipeline.

## Model Migration Notes

The dashboard copy and result cards now describe the backend as a `DenseNet121-v2` transfer learning model with GradCAM explainability. The frontend request flow is unchanged: uploads are still sent as `multipart/form-data` to the FastAPI backend.

Frontend-facing model details:

- Architecture: DenseNet121
- Training approach: transfer learning and fine-tuning
- Explainability: GradCAM heatmap overlays
- Backend input size: `224x224`
- Prediction labels: `NORMAL` and `PNEUMONIA`

## Getting Started

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Required Environment

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Verification

```bash
npm run lint
npm run build
```

## Medical Imaging UX

GradCAM text is intentionally framed as model attention/explainability rather than clinical proof. The frontend should continue to show the medical disclaimer with every result.

## Deploy

Set `NEXT_PUBLIC_API_URL` to the deployed FastAPI backend URL. Keep Supabase service-role keys only on the backend.
