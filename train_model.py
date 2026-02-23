import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("trained_dataset.csv")

# Safety check
required_cols = {"resume", "shortlisted"}
if not required_cols.issubset(df.columns):
    raise Exception("CSV must contain resume & shortlisted columns")

# Fill missing text
df["resume"] = df["resume"].fillna("")

X_text = df["resume"]
y = df["shortlisted"]

# Convert resume text → numeric features
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)

X = vectorizer.fit_transform(X_text)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train AI model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"✅ AI Model Accuracy: {accuracy:.2f}")

# Save model & vectorizer
joblib.dump(model, "ai_shortlist_model.pkl")
joblib.dump(vectorizer, "resume_vectorizer.pkl")

print("🎯 Resume AI trained & saved successfully")
