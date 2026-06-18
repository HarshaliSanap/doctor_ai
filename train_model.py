import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Load dataset
df = pd.read_csv("doctor_specialty_dataset.csv")

# Create model
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Train model
model.fit(df["report"], df["specialty"])

# Save model
joblib.dump(model, "doctor_model.pkl")

print("Model trained successfully!")