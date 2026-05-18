<div align="center">

<br/>

```
██████╗ ███╗   ██╗███████╗██╗   ██╗███╗   ███╗ ██████╗ ███████╗ ██████╗ █████╗ ███╗   ██╗
██╔══██╗████╗  ██║██╔════╝██║   ██║████╗ ████║██╔═══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║
██████╔╝██╔██╗ ██║█████╗  ██║   ██║██╔████╔██║██║   ██║███████╗██║     ███████║██╔██╗ ██║
██╔═══╝ ██║╚██╗██║██╔══╝  ██║   ██║██║╚██╔╝██║██║   ██║╚════██║██║     ██╔══██║██║╚██╗██║
██║     ██║ ╚████║███████╗╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████║╚██████╗██║  ██║██║ ╚████║
╚═╝     ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
```

# 🩺 PneumoScan AI

### AI-Powered Pneumonia Detection from Chest X-Rays

**DenseNet121 · GradCAM Explainability · FastAPI · Next.js · Supabase**

<br/>

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

<br/>

> A production-ready full-stack healthcare AI platform for Pneumonia detection from Chest X-ray images using **DenseNet121** deep learning with **Grad-CAM** explainability, designed for clinical interpretability and trust.

<br/>

</div>

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Project Evolution](#-project-evolution)
- [Repository Structure](#-repository-structure)
- [AI Model Architecture](#-ai-model-architecture)
- [Grad-CAM Explainability](#-grad-cam-explainability)
- [Tech Stack](#-tech-stack)
- [Features](#-features)
- [Local Development Setup](#-local-development-setup)
- [Environment Variables](#-environment-variables)
- [Dataset](#-dataset)
- [Deployment](#-deployment)
- [Screenshots](#-screenshots)
- [Future Improvements](#-future-improvements)
- [Author](#-author)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 🧭 Project Overview

**PneumoScan AI** is a full-stack clinical AI platform that detects Pneumonia from Chest X-ray images with deep learning and provides **visual explainability** through Grad-CAM heatmaps — making AI decisions interpretable for medical professionals.

The system supports the full diagnostic workflow:

- 📤 Upload a Chest X-ray
- 🧠 Get an AI prediction with confidence score and severity level
- 🔥 View a Grad-CAM heatmap overlaid on the X-ray showing the model's attention regions
- 📊 Access full prediction history with timestamps
- ☁️ Persistent storage of images and results via Supabase

---

## 📌 Project Evolution

### 🔹 Version 1 — Legacy Prototype

A simple CNN-based proof-of-concept built rapidly in Google Colab and deployed via Streamlit.

| Property | Details |
|---|---|
| Location | `legacy-version/` |
| Framework | TensorFlow / Keras + Streamlit |
| Input Size | 150×150 |
| Architecture | Custom CNN (Conv2D → MaxPool → Dense) |
| Explainability | None |

**Features:** Upload X-ray · Basic CNN prediction · Streamlit UI

---

### 🚀 Version 2 — PneumoScan AI (Current)

A fully rebuilt, production-style system with a decoupled frontend/backend architecture, upgraded AI model, and Grad-CAM explainability.

| Property | Details |
|---|---|
| Location | `pneumoscan-ai/` |
| Backend | FastAPI |
| Frontend | Next.js 15 + TypeScript |
| Input Size | 224×224 (DenseNet121 native) |
| Architecture | **DenseNet121** (ImageNet pretrained, fine-tuned) |
| Explainability | **Grad-CAM** heatmap overlays |
| Storage | Supabase PostgreSQL + Storage Buckets |

---

## 🏗 Repository Structure

```
Pneumonia_X-tray_Detection/
│
├── legacy-version/                          # Version 1 — Streamlit prototype
│   ├── app.py
│   ├── requirements.txt
│   ├── Automated_Pneumonia_Detection_from_Chest_X_Ray_Images.ipynb
│   └── README_OLD.md
│
├── pneumoscan-ai/                           # Version 2 — Production platform
│   │
│   ├── backend/                             # FastAPI AI backend
│   │   ├── app/
│   │   │   ├── main.py                      # FastAPI entry point
│   │   │   ├── routes/
│   │   │   │   ├── predict.py               # /predict endpoint
│   │   │   │   └── history.py               # /history endpoint
│   │   │   ├── services/
│   │   │   │   ├── model_service.py         # DenseNet121 inference
│   │   │   │   ├── gradcam_service.py       # Grad-CAM pipeline
│   │   │   │   └── supabase_service.py      # Storage + DB operations
│   │   │   └── core/
│   │   │       └── config.py                # Environment config
│   │   ├── models/
│   │   │   └── pneumoscan_densenet121.h5    # Trained model weights
│   │   └── requirements.txt
│   │
│   └── frontend/                            # Next.js frontend
│       ├── app/
│       │   ├── page.tsx                     # Dashboard / Home
│       │   ├── predict/page.tsx             # Upload & prediction page
│       │   └── history/page.tsx             # Prediction history
│       ├── components/
│       │   ├── UploadZone.tsx
│       │   ├── PredictionCard.tsx
│       │   ├── GradCamViewer.tsx
│       │   └── HistoryTable.tsx
│       ├── public/
│       ├── next.config.ts
│       ├── tailwind.config.ts
│       └── package.json
│
├── screenshots/
│
├── README.md
└── .gitignore
```

---

## 🧠 AI Model Architecture

PneumoScan AI uses **DenseNet121** — a densely connected convolutional network pretrained on ImageNet — fine-tuned on the Chest X-ray Pneumonia dataset for binary classification.

### Why DenseNet121?

| Property | DenseNet121 | Previous CNN |
|---|---|---|
| Input resolution | 224×224 | 150×150 |
| Pretrained weights | ✅ ImageNet | ❌ From scratch |
| Skip connections | ✅ Dense blocks | ❌ None |
| GradCAM quality | ✅ Excellent (`conv5_block16_concat`) | ⚠️ Poor |
| AUC-ROC | ~0.97+ | ~0.88 |
| Clinical trust | ✅ High | ❌ Low |

### Model Pipeline

```
Input (224×224×3)
       │
       ▼
┌─────────────────────────────────────────┐
│          DenseNet121 Backbone           │
│         (ImageNet pretrained)           │
│                                         │
│  Dense Block 1 → Transition Layer       │
│  Dense Block 2 → Transition Layer       │
│  Dense Block 3 → Transition Layer       │
│  Dense Block 4  ← GradCAM anchor here  │
│        conv5_block16_concat             │
└─────────────────────────────────────────┘
       │
       ▼
  GlobalAveragePooling2D
       │
       ▼
  BatchNormalization
       │
       ▼
  Dense(512, ReLU)
       │
       ▼
  Dropout(0.4)
       │
       ▼
  Dense(256, ReLU)
       │
       ▼
  Dropout(0.2)
       │
       ▼
  Dense(1, Sigmoid)
       │
       ▼
  NORMAL / PNEUMONIA
```

### Two-Phase Training Strategy

```
Phase 1 — Head Training (Frozen Backbone)
  Epochs : 15
  LR     : 1e-3
  Frozen : All DenseNet121 layers
  Goal   : Train new classification head safely

Phase 2 — Fine-Tuning (Partial Unfreeze)
  Epochs : 20
  LR     : 1e-5
  Frozen : First 300 layers only
  Goal   : Gently adapt deep DenseNet features to X-ray domain
```

### Training Configuration

```python
Optimizer   : Adam
Loss        : Binary Cross-Entropy
Metrics     : Accuracy, AUC-ROC, Precision, Recall
Augmentation: Rotation ±15°, Shift ±10%, Zoom ±15%,
              Horizontal Flip, Brightness [0.85–1.15]
Class Weight: Balanced (auto-computed — handles dataset imbalance)
Callbacks   : EarlyStopping · ReduceLROnPlateau · ModelCheckpoint
```

---

## 🔥 Grad-CAM Explainability

PneumoScan AI uses **Gradient-weighted Class Activation Mapping (Grad-CAM)** to visualise which regions of the X-ray influenced the model's prediction.

### How It Works

```
1. Forward pass → record activations at conv5_block16_concat
2. GradientTape → compute ∂(prediction score) / ∂(feature map)
3. Global average pool gradients → per-channel importance weights
4. Weight each channel of the feature map
5. Apply ReLU → normalize → resize to 224×224
6. Apply JET colormap → overlay on original X-ray
```

### What Grad-CAM Reveals

| Heatmap Region | Clinical Meaning |
|---|---|
| 🔴 Red / Hot areas | Regions most responsible for the prediction |
| 🟡 Yellow areas | Moderate model attention |
| 🔵 Cool / Blue areas | Low model attention |

For **Pneumonia** cases, heatmaps typically highlight:
- Consolidation areas in the lower lobes
- Perihilar infiltrates
- Opacity regions consistent with infection

> Grad-CAM anchor layer: `conv5_block16_concat` — the final dense block output of DenseNet121, chosen for optimal spatial resolution and semantic depth.

---

## ⚙️ Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **TensorFlow 2.x / Keras** | DenseNet121 model inference |
| **OpenCV** | Grad-CAM heatmap generation & image processing |
| **Pillow** | Image loading and preprocessing |
| **Supabase Python SDK** | Database + Storage integration |
| **Uvicorn** | ASGI server |

### Frontend

| Technology | Purpose |
|---|---|
| **Next.js 15** | React framework (App Router) |
| **TypeScript** | Type-safe frontend development |
| **Tailwind CSS** | Utility-first styling |
| **Framer Motion** | Animations and transitions |
| **React Dropzone** | Drag-and-drop X-ray upload |

### Infrastructure

| Technology | Purpose |
|---|---|
| **Supabase PostgreSQL** | Prediction history & metadata |
| **Supabase Storage** | X-ray images + Grad-CAM outputs |
| **Vercel** | Frontend hosting |
| **Render** | Backend hosting |

### AI / ML

| Technology | Purpose |
|---|---|
| **DenseNet121** | Core classification model |
| **ImageNet Weights** | Transfer learning baseline |
| **Grad-CAM** | Explainability heatmaps |
| **scikit-learn** | Evaluation metrics (AUC, confusion matrix) |

---

## ✅ Features

### 🧠 AI Prediction
Upload any chest X-ray and receive:
- **Prediction label** — NORMAL or PNEUMONIA
- **Confidence score** — probability from the sigmoid output
- **Severity indicator** — derived from confidence threshold bands

### 🔥 Grad-CAM Heatmap
Visual explanation showing:
- Infected lung regions highlighted in the X-ray
- Model attention map overlaid with JET colormap
- Side-by-side: Original · Heatmap · Overlay

### 📊 Prediction History Dashboard
Persistent storage of:
- Uploaded X-ray images
- Prediction label and confidence
- Grad-CAM heatmap outputs
- Timestamps

### 🎨 Interactive UI
- Drag-and-drop X-ray upload with preview
- Animated prediction results
- Upload progress indicator
- Responsive design for all screen sizes
- Analytics summary cards

---

## 🛠 Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Conda (recommended) or virtualenv
- Supabase account and project

---

### 1. Clone the Repository

```bash
git clone https://github.com/dilutha/Pneumonia_X-tray_Detection.git
cd Pneumonia_X-tray_Detection
```

---

### 2. Backend Setup

```bash
cd pneumoscan-ai/backend

# Create and activate conda environment
conda create -n pneumoscan python=3.11
conda activate pneumoscan

# Install dependencies
pip install -r requirements.txt
```

Create your `.env` file (see [Environment Variables](#-environment-variables) below), then run:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Backend API runs at: **http://localhost:8000**

Interactive API docs at: **http://localhost:8000/docs**

---

### 3. Frontend Setup

```bash
cd pneumoscan-ai/frontend

# Install dependencies
npm install

# Start development server
npx next dev --webpack
```

Frontend runs at: **http://localhost:3000**

> **Note:** The `--webpack` flag is required to use the Webpack bundler instead of Turbopack, ensuring full compatibility with all project dependencies.

---

### 4. Model Training (Optional — Google Colab)

To retrain or fine-tune the DenseNet121 model:

1. Open `pneumoscan_densenet121_gradcam.py` in Google Colab
2. Mount your Google Drive and upload the dataset zip to `MyDrive/archive-7.zip`
3. Run all cells — the trained model saves to `MyDrive/pneumoscan_densenet121_best.h5`
4. Download and place in `pneumoscan-ai/backend/models/`

---

## 🌐 Environment Variables

### Backend — `pneumoscan-ai/backend/.env`

```env
APP_NAME="PneumoScan AI"
MODEL_PATH="models/pneumoscan_densenet121_best.h5"
MODEL_INPUT_SIZE=224
GRADCAM_LAYER="conv5_block16_concat"

SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
SUPABASE_BUCKET=xray-uploads
```

### Frontend — `pneumoscan-ai/frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Dataset

**Chest X-Ray Images (Pneumonia)** from Kaggle

| Property | Value |
|---|---|
| Source | [Kaggle — Chest X-ray Pneumonia](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) |
| Classes | NORMAL · PNEUMONIA |
| Train set | ~5,216 images |
| Validation | ~16 images |
| Test set | ~624 images |
| Format | JPEG, grayscale X-rays |

> The class imbalance (more PNEUMONIA than NORMAL samples) is automatically handled during training via `compute_class_weight("balanced")`.

---

## ☁️ Deployment

Recommended production stack:

| Component | Platform | Notes |
|---|---|---|
| **Frontend** | [Vercel](https://vercel.com) | Auto-deploy from GitHub |
| **Backend** | [Render](https://render.com) | Python 3.11 runtime |
| **Database** | [Supabase](https://supabase.com) | PostgreSQL + Storage |
| **Model** | Bundled with backend | `.h5` file in repo or cloud storage |

### Frontend Deploy (Vercel)

```bash
npx vercel --prod
```

Set `NEXT_PUBLIC_API_URL` to your Render backend URL in Vercel project settings.

### Backend Deploy (Render)

- Runtime: Python 3.11
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- Set all environment variables in Render dashboard

---

## 📷 Screenshots

Place screenshots in the `screenshots/` directory.

| Screenshot | Filename |
|---|---|
| Dashboard overview | `screenshots/dashboard.png` |
| X-ray upload interface | `screenshots/upload.png` |
| Grad-CAM result view | `screenshots/gradcam.png` |
| Prediction history | `screenshots/history.png` |

---

## 📌 Future Improvements

- [ ] **Multi-class lung disease classification** (COVID-19, TB, Pleural Effusion)
- [ ] **EfficientNetV2 migration** for further accuracy gains
- [ ] **PDF medical report generation** with prediction summary
- [ ] **User authentication** with Supabase Auth
- [ ] **Real-time analytics** dashboard with charts
- [ ] **Docker + docker-compose** for one-command local setup
- [ ] **CI/CD pipelines** via GitHub Actions
- [ ] **Model versioning** and A/B evaluation framework
- [ ] **DICOM file support** for direct radiology system integration
- [ ] **Research paper integration** and reference citation display

---

## 👨‍💻 Author

<div align="center">

**Dilutha Weerasinghe**

🎓 Undergraduate Researcher

BSc (Hons) Data Science · BSc (Hons) Business Information Systems

[![GitHub](https://img.shields.io/badge/GitHub-dilutha-181717?style=for-the-badge&logo=github)](https://github.com/dilutha)

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ⭐ Acknowledgements

- [TensorFlow](https://tensorflow.org) & [Keras](https://keras.io) — Deep learning framework
- [DenseNet Paper](https://arxiv.org/abs/1608.06993) — Huang et al., "Densely Connected Convolutional Networks"
- [Grad-CAM Paper](https://arxiv.org/abs/1610.02391) — Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks"
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python API framework
- [Next.js](https://nextjs.org) — React production framework
- [Supabase](https://supabase.com) — Open-source Firebase alternative
- [Kaggle Chest X-ray Dataset](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) — Paul Mooney

---

<div align="center">

*Built with ❤️ for interpretable clinical AI*

**PneumoScan AI — Making AI Decisions Visible to the People Who Matter**

</div>
