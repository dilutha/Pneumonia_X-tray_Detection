# 🩺 PneumoScan AI — Pneumonia Detection Platform
 
An AI-powered full-stack healthcare platform for detecting Pneumonia from Chest X-ray images using Deep Learning and Explainable AI (Grad-CAM).
 
This repository contains both:
 
- 📦 Legacy Streamlit Prototype
- 🚀 Rebuilt Production-Style Full Stack AI Platform
---
 
## 📌 Project Evolution
 
### 🔹 Version 1 — Legacy Prototype
 
A simple CNN-based Pneumonia Detection system built using:
 
- TensorFlow / Keras
- Google Colab
- Streamlit
**Location:**
 
```text
legacy-version/
```
 
**Features:**
 
- Upload X-ray image
- Basic CNN prediction
- Streamlit interface
---
 
### 🔹 Version 2 — PneumoScan AI (Rebuilt System)
 
A modern AI healthcare platform with:
 
- ⚡ FastAPI backend
- 🎨 Next.js frontend
- 🧠 CNN-based Pneumonia Detection
- 🔥 Grad-CAM Explainability
- ☁️ Supabase Storage + Database
- 📊 Prediction History Dashboard
- 📡 REST API Architecture
- 🌐 Production-ready Full Stack Design
**Location:**
 
```text
pneumoscan-ai/
```
 
---
 
## 🏗 Repository Structure
 
```text
Pneumonia_X-tray_Detection/
│
├── legacy-version/
│   ├── app.py
│   ├── requirements.txt
│   ├── Automated_Pneumonia_Detection_from_Chest_X_Ray_Images.ipynb
│   └── README_OLD.md
│
├── pneumoscan-ai/
│   ├── backend/
│   └── frontend/
│
├── screenshots/
│
├── README.md
└── .gitignore
```
 
---
 
## 🧠 AI Model Architecture
 
The CNN model is trained using Chest X-ray images for binary classification:
 
- **NORMAL**
- **PNEUMONIA**
### CNN Architecture
 
```
Input (150x150x3)
↓
Conv2D + ReLU
↓
MaxPooling
↓
Conv2D + ReLU
↓
MaxPooling
↓
Conv2D + ReLU
↓
Flatten
↓
Dense + Dropout
↓
Sigmoid Output
```
 
---
 
## 🔥 Explainable AI — Grad-CAM
 
The rebuilt platform includes Grad-CAM visualization to highlight:
 
- Infected lung regions
- CNN attention areas
- Model explainability
This improves interpretability of AI predictions.
 
---
 
## ⚙️ Tech Stack
 
### Frontend
 
- Next.js 15
- TypeScript
- Tailwind CSS
- Framer Motion
- React Dropzone
### Backend
 
- FastAPI
- TensorFlow / Keras
- OpenCV
- Pillow
- Supabase Python SDK
### Database & Storage
 
- Supabase PostgreSQL
- Supabase Storage Buckets
### AI / ML
 
- CNN
- Grad-CAM
- TensorFlow
- Keras
---
 
## 🚀 Features
 
### ✅ AI Prediction
 
Upload chest X-ray images and receive:
 
- Prediction label
- Confidence score
- Severity level
### ✅ Grad-CAM Heatmap
 
Visual explanation showing:
 
- Infected lung regions
- Model attention map
### ✅ Prediction History
 
Stores:
 
- Uploaded images
- Predictions
- Confidence
- Timestamps
- Grad-CAM outputs
### ✅ Interactive Dashboard
 
Modern UI with:
 
- Animations
- Upload progress
- Responsive design
- Analytics cards
---
 
## 📷 Screenshots
 
Add screenshots inside:
 
```text
screenshots/
```
 
Suggested screenshots:
 
- Dashboard
- Upload interface
- Grad-CAM result
- Prediction history
---
 
## 🛠 Local Development
 
### 1. Clone Repository
 
```bash
git clone https://github.com/dilutha/Pneumonia_X-tray_Detection.git
```
 
### 2. Backend Setup
 
```bash
cd pneumoscan-ai/backend
conda create -n pneumoscan python=3.11
conda activate pneumoscan
pip install -r requirements.txt
```
 
**Run backend:**
 
```bash
python -m uvicorn app.main:app --reload --port 8000
```
 
Backend runs on: `http://localhost:8000`
 
### 3. Frontend Setup
 
```bash
cd pneumoscan-ai/frontend
npm install
npm run dev
```
 
Frontend runs on: `http://localhost:3000`
 
---
 
## 🌐 Environment Variables
 
### Backend `.env`
 
```env
APP_NAME="PneumoScan AI"
MODEL_INPUT_SIZE=150
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
SUPABASE_SERVICE_KEY=your-service-key
```
 
### Frontend `.env.local`
 
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
 
---
 
## 📊 Dataset
 
**Dataset used:** Chest X-ray Images (Pneumonia)
 
**Source:** Kaggle Chest X-ray Dataset
 
**Classes:**
 
- NORMAL
- PNEUMONIA
---
 
## ☁️ Deployment
 
Recommended deployment stack:
 
| Service  | Platform  |
|----------|-----------|
| Frontend | Vercel    |
| Backend  | Render    |
| Database | Supabase  |
 
---
 
## 📌 Future Improvements
 
- DenseNet121 / EfficientNet migration
- Multi-class lung disease classification
- PDF medical reports
- User authentication
- Real-time analytics
- Docker deployment
- CI/CD pipelines
- Research paper integration
---
 
## 👨‍💻 Author
 
**Dilutha Weerasinghe**
 
🎓 Undergraduate
 
- BSc (Hons) Data Science
- BSc (Hons) Business Information Systems
---
 
## 📄 License
 
This project is licensed under the **MIT License**.
 
---
 
## ⭐ Acknowledgements
 
- TensorFlow
- Keras
- FastAPI
- Next.js
- Supabase
- Grad-CAM Research Paper
- Kaggle Chest X-ray Dataset
 
