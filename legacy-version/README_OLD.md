## 🩻 X-ray Pneumonia Detection System

An AI-powered deep learning web app for detecting **Pneumonia from chest X-ray images** using a Convolutional Neural Network (CNN) architecture. The model is trained in **Google Colab** and deployed via an interactive **Streamlit** web app.

---

## 🧠 Model Architecture

The model is a simple CNN with:
- 3 Convolutional layers
- 3 MaxPooling layers
- Flatten and Fully Connected layers
- Binary classification (Pneumonia vs Normal)

### CNN Architecture Summary

Input Layer (X-ray image 150x150x1)
→ Conv2D (32 filters, 3x3) + ReLU
→ MaxPooling2D (2x2)
→ Conv2D (64 filters, 3x3) + ReLU
→ MaxPooling2D (2x2)
→ Conv2D (128 filters, 3x3) + ReLU
→ MaxPooling2D (2x2)
→ Flatten
→ Dense (128) + ReLU
→ Dense (1) + Sigmoid


---

## 🛠 Tools & Technologies

- 💻 **Google Colab** – for model training (TensorFlow/Keras)
- 🌐 **Streamlit** – for building the web interface
- 🧾 **Python** – core language
- 📦 Libraries: `tensorflow`, `keras`, `matplotlib`, `numpy`, `pillow`, `streamlit`

---

## 📁 Dataset

Dataset: [Chest X-ray Images (Pneumonia) - Kaggle](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia)

Structure:
chest_xray/
├── train/
│ ├── NORMAL/
│ └── PNEUMONIA/
├── val/
│ ├── NORMAL/
│ └── PNEUMONIA/
└── test/
├── NORMAL/
└── PNEUMONIA/


---

## 🚀 How to Run

### 🔧 Model Training (Google Colab)

1. Open the `Xray_Pneumonia_CNN.ipynb` in Google Colab.
2. Upload the dataset or mount Google Drive.
3. Train the CNN model.
4. Save the trained `.h5` model file:
   ```python
   model.save('pneumonia_cnn_model.h5')
🖥️ Streamlit Web App
Clone this repo or download the files.
Place the pneumonia_cnn_model.h5 file in the root folder.
Install required packages:
pip install streamlit tensorflow pillow
Run the app:
streamlit run app.py
📸 Web App Features

Upload an X-ray image (JPG/PNG)
Model predicts Normal or Pneumonia
Displays uploaded image and prediction result
🧪 Sample Prediction

X-ray Image	Model Prediction
🚨 Pneumonia Detected
📌 Future Improvements

Improve model accuracy with deeper CNN or transfer learning (e.g., ResNet)
Add Grad-CAM visualization for model explainability
Add confidence score and batch upload feature
Deploy via HuggingFace Spaces or AWS

👤 Author

Dilutha Weerasinghe 
🎓 Undergraduate – BSc (Hons) in Data Science and Bsc (Hons) Business Information Systems
🔗 LinkedIn | GitHub

📄 License

This project is open source under the MIT License.
