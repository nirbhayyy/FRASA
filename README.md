# FRASA — Fake Review Detection & Sentiment Analysis

FRASA is a machine learning powered web application for analyzing online reviews.

The application combines **fake review detection** and **sentiment analysis** with a Django-based web interface. Users can submit review text and receive a prediction along with confidence information and sentiment analysis.

---

## 🚀 Features

- 🔍 Fake review detection
- ✅ Genuine/Fake review classification
- 😊 Sentiment analysis
- 📊 Prediction confidence
- 📈 Review analytics dashboard
- 📝 Review history
- 👤 User authentication
- 🔌 Django REST API
- 🤖 Machine learning model integration
- 🧹 NLP-based text preprocessing

---

## 🧠 Machine Learning

### Fake Review Detection

The project experiments with multiple machine learning algorithms:

- Logistic Regression
- Random Forest
- XGBoost
- Support Vector Machine
- Ensemble Model

### Sentiment Analysis

The sentiment analysis component uses:

- Multinomial Naive Bayes
- Linear Support Vector Classifier (LinearSVC)

### NLP Techniques

The text processing pipeline includes:

- Text cleaning
- Lowercasing
- Stopword removal
- Stemming
- Bag of Words
- TF-IDF
- N-gram features

---

## 📊 Model Performance

The following results were obtained during model evaluation:

| Model | Accuracy |
|---|---:|
| Logistic Regression | 87.38% |
| Random Forest | 85.52% |
| XGBoost | 85.37% |
| Support Vector Machine | 87.83% |

> Model performance can vary depending on the dataset, preprocessing pipeline, train/test split, and evaluation configuration.

---

## 🛠️ Tech Stack

### Backend

- Python
- Django
- Django REST Framework

### Machine Learning & NLP

- Scikit-learn
- Pandas
- NumPy
- NLTK
- XGBoost

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js

### Database

- SQLite

### Development & Model Management

- Git
- Git LFS
- Jupyter Notebooks

---

## 🏗️ Project Architecture

```text
User
  │
  ▼
Django Web Interface
  │
  ▼
Django REST API
  │
  ├───────────────┐
  ▼               ▼
Fake Review     Sentiment
Detection       Analysis
  │               │
  ▼               ▼
ML Models       ML Model
  │               │
  └───────┬───────┘
          ▼
     Prediction
          │
          ▼
     Dashboard