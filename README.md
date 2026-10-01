# FRASA — Fake Review Detection & Sentiment Analysis

FRASA is a machine learning based web application that detects fake
reviews and performs sentiment analysis on review text.

The application integrates trained NLP and machine learning models
with a Django web application to provide review classification,
sentiment prediction, confidence scores, and review analytics.

## 🚀 Features

- Fake review detection
- Genuine/fake classification
- Sentiment analysis
- Prediction confidence
- Review history
- Dashboard and analytics
- User authentication
- Django REST API
- Machine learning model integration
- NLP-based text preprocessing

## 🧠 Machine Learning

### Fake Review Detection

The project experiments with multiple machine learning algorithms:

- Logistic Regression
- Random Forest
- XGBoost
- Support Vector Machine
- Ensemble model

### Sentiment Analysis

The project uses machine learning models for sentiment classification,
including:

- Multinomial Naive Bayes
- Linear SVC

### NLP Techniques

- Text preprocessing
- Lowercasing
- Stopword removal
- Stemming
- Bag of Words
- TF-IDF
- N-gram features

## 🛠️ Tech Stack

### Backend

- Python
- Django
- Django REST Framework

### Machine Learning

- Scikit-learn
- Pandas
- NumPy
- NLTK
- XGBoost
- Joblib

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js

### Database

- SQLite

## 📂 Project Structure

```text
FRASA/
│
├── FAKEreview/
│   ├── Analyzer/
│   ├── api/
│   ├── FAKEreview/
│   ├── ml_models/
│   └── manage.py
│
├── notebooks/
│   ├── review_model.ipynb
│   └── sentiment_model.ipynb
│
├── .gitattributes
├── .gitignore
├── README.md
└── requirements.txt