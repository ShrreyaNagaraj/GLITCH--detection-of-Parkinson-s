import streamlit as st
import cv2
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def process_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return edges

def extract_features(edges):
    return np.count_nonzero(edges) if edges is not None else 0

def load_dataset(base_path, dataset_type="training"):
    dataset_path = os.path.join(base_path, "spiral", dataset_type)
    healthy_path = os.path.join(dataset_path, "healthy")
    parkinson_path = os.path.join(dataset_path, "parkinson")

    if not os.path.exists(healthy_path) or not os.path.exists(parkinson_path):
        return np.array([]), np.array([])

    X, y = [], []

    for category, label in [(healthy_path, 0), (parkinson_path, 1)]:
        images = [f for f in os.listdir(category) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for image_file in images:
            img_path = os.path.join(category, image_file)
            edges = process_image(img_path)
            if edges is not None:
                X.append(extract_features(edges))
                y.append(label)

    return np.array(X).reshape(-1, 1), np.array(y)  # Fix: Reshaping X to 2D

def train_model(X, y):
    if len(X) == 0:
        return None, 0.0

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, accuracy

st.title("Parkinson's Detection - Spiral Drawing Analysis")
st.write("Upload a spiral drawing image to analyze its quality and detect Parkinson's risk.")

dataset_path = r"C:\Users\Siya\Desktop\spiral\archive"

st.write("Loading dataset and training model...")
X_train, y_train = load_dataset(dataset_path, "training")
X_test, y_test = load_dataset(dataset_path, "testing")

if len(X_train) > 0:
    model, accuracy = train_model(X_train, y_train)
    st.write(f"Model trained successfully! Accuracy: {accuracy * 100:.2f}%")
else:
    st.write("Error: No training data found!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None and model is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        st.image(edges, caption="Edge Detected Image", channels="GRAY")

        feature = np.array([extract_features(edges)]).reshape(1, -1)  # Fix: Reshaping input
        prediction = model.predict(feature)
        risk = "Healthy" if prediction[0] == 0 else "Parkinson's Risk Detected"

        st.write(f"Assessment: {risk}")
    else:
        st.write("Error: Could not read uploaded image!")
else:
    st.write("Please upload an image to analyze.")
