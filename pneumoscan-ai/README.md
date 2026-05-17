# PneumoScan AI

PneumoScan AI is an AI-assisted chest X-ray pneumonia detection platform built with FastAPI, TensorFlow/Keras, Next.js App Router, TailwindCSS, Supabase Storage, and PostgreSQL.

## DenseNet121 Migration

The application has been migrated from the original custom CNN pipeline using `150x150` inputs to a DenseNet121 transfer learning pipeline using `224x224` inputs.

The model artifact is intentionally not included in this migration. Place the new DenseNet121 `.h5` file at the path configured by:

```bash
MODEL_PATH="ml_models/densenet121_pneumonia_model.h5"
MODEL_INPUT_SIZE=224
MODEL_VERSION="DenseNet121-v2"
GRADCAM_LAYER_NAME="conv5_block16_concat"
```

## Why DenseNet121

DenseNet121 is a stronger backbone for medical imaging than the old small custom CNN because it reuses dense feature connections learned from large-scale image data. With transfer learning and fine-tuning, the model can preserve low-level visual features such as edges and textures while adapting deeper layers to chest X-ray pneumonia patterns.

Benefits of the migration:

- Higher-capacity feature extraction for subtle lung opacity patterns.
- Better transfer learning behavior from ImageNet-pretrained visual features.
- `224x224` input resolution, matching DenseNet121 preprocessing expectations.
- DenseNet-compatible TensorFlow preprocessing via `tf.keras.applications.densenet.preprocess_input`.
- Explainable AI support through GradCAM at `conv5_block16_concat`.
- Cleaner model metadata using `DenseNet121-v2`.

## Inference Flow

1. The frontend uploads a JPEG, PNG, or WebP chest X-ray as `multipart/form-data`.
2. FastAPI validates file type, file size, and image integrity.
3. The image is converted to RGB, resized to `224x224`, and passed through DenseNet121 preprocessing.
4. TensorFlow/Keras runs binary inference.
5. The API maps the probability to `NORMAL` or `PNEUMONIA`.
6. GradCAM uses `conv5_block16_concat` to generate an explainability overlay.
7. Supabase Storage stores the original image and heatmap.
8. Supabase/PostgreSQL stores prediction history.

The public API contract is unchanged: upload requests, prediction responses, history responses, and health responses keep the same shapes.

## Local Commands

Backend:

```bash
cd backend
source .venv312/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Verification:

```bash
cd backend
python -m compileall app
```

```bash
cd frontend
npm run lint
npm run build
```

## Production Notes

- Do not commit `.env`, Supabase service-role keys, or `.h5` model files.
- Store the DenseNet121 model in private object storage, a Render disk, or another controlled deployment artifact path.
- Keep `MODEL_INPUT_SIZE=224`; changing it will break DenseNet121 model compatibility.
- Monitor recall, precision, AUC, and false-negative rate on a held-out medical validation set before clinical use.
- GradCAM is an explainability aid, not a diagnosis by itself.
