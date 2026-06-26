# Lung Disease Detection System

An AI-based clinical support platform developed using Deep Learning and Computer Vision techniques to analyze chest X-ray images and assist medical professionals in the early and accurate diagnosis of respiratory conditions.

---

## 🚀 Project Overview
Lung diseases such as pneumonia and tuberculosis are major global health concerns. This project presents a doctor-centered clinical support system that automatically classifies chest X-ray images to streamline diagnostic workflows and improve accessibility to critical healthcare services. 

The application is built using a robust full-stack architecture, featuring a deep learning backend integrated with a secure relational database to manage patient records, visual explanations, and final medical reports.

---

## 🧠 Model Architecture & Core AI Techniques
* **Transfer Learning Core:** The system leverages the **EfficientNetV2-B3** architecture using TensorFlow and Keras, optimized for high parameter efficiency, faster training phases, and superior feature extraction.
* **Multi-Class Classification:** Images are automatically classified into five categories:
  * **Normal:** Clear lung fields with no visible abnormalities.
  * **Pneumonia:** Signs of localized or widespread pulmonary inflammation.
  * **Tuberculosis:** Indicative patterns of active bacterial infection.
  * **Nodule:** Small, round, or oval growths constituting localized abnormalities that may warrant further diagnostic follow-ups (e.g., CT scans or biopsies).
  * **Unknown:** Ambiguous cases or images falling outside standard diagnostic thresholds.
* **Performance Optimization:** To combat overfitting and improve generalization across diverse clinical datasets, the model integrates:
  * Data Augmentation & Batch Normalization
  * Dropout Layers & L2 Regularization
  * Early Stopping mechanisms during training

---

## 🔧 Image Preprocessing Pipeline
To maximize model accuracy and reliability, incoming chest X-rays undergo an advanced preprocessing workflow:
1. **Spatial Standardization:** Images are resized to a uniform dimension of 300×300 pixels.
2. **Contrast Enhancement:** **Contrast Limited Adaptive Histogram Equalization (CLAHE)** is applied to enhance hidden structural details and local contrast in low-quality radiographs.
3. **Normalization:** Scale adjustments are performed natively via standard EfficientNet preprocessing layers.

---

## 👁️ Explainable AI (XAI) & Clinical Trust
To ensure transparency and bridge the gap between machine learning and clinical trust, the system integrates **LIME (Local Interpretable Model-Agnostic Explanations)**. 
* **Feature Visualization:** LIME highlights the exact sub-regions and pixel segments of the X-ray image that influenced the network's prediction.
* **Doctor Verification:** This clinical interpretability allows physicians to visually cross-verify the AI’s logical reasoning against established radiological benchmarks.

---

## 💻 Tech Stack
* **Backend:** Django REST Framework (DRF) handling API routing, AI model inference, and medical logic.
* **Frontend:** Standard web technologies (HTML5, CSS3, JavaScript) providing an intuitive interface for uploading images, viewing confidence scores, and generating downloadable patient reports.
* **Database:** Relational Database Management System (RDBMS) for secure tracking of patient records and diagnostic history.
* **Dataset Source:** Publicly available clinical datasets compiled from open-source biomedical platforms like Kaggle.
