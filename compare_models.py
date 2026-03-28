import cv2
import numpy as np
import tensorflow as tf
import pickle
import json

def crop_face(img_bgr):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0: return img_bgr
    x, y, w, h = max(faces, key=lambda b: b[2]*b[3])
    pad = int(0.2 * w)
    x1, y1 = max(0, x - pad), max(0, y - pad)
    x2, y2 = min(img_bgr.shape[1], x + w + pad), min(img_bgr.shape[0], y + h + pad)
    return img_bgr[y1:y2, x1:x2]

img_bgr = cv2.imread('anji.jpg.png')
img_face = crop_face(img_bgr)

print("--- Testing model.h5 (224x224, full image) ---")
try:
    m1 = tf.keras.models.load_model('model.h5')
    img1 = cv2.cvtColor(cv2.resize(img_bgr, (224, 224)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    pred1 = m1.predict(np.expand_dims(img1, axis=0))[0]
    classes1 = ["acne", "blackheads", "darkspots", "pores", "wrinkles"]
    print(f"Top: {classes1[np.argmax(pred1)]} ({np.max(pred1)*100:.2f}%)")
    for c, p in zip(classes1, pred1): print(f"{c}: {p*100:.2f}%")
except Exception as e: print("m1 err:", e)

print("\n--- Testing skin_model.h5 (128x128, cropped face) ---")
try:
    m2 = tf.keras.models.load_model('skin_model.h5')
    img2 = cv2.cvtColor(cv2.resize(img_face, (128, 128)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    pred2 = m2.predict(np.expand_dims(img2, axis=0))[0]
    with open('classes.json') as f: classes2 = json.load(f)
    print(f"Top: {classes2[np.argmax(pred2)]} ({np.max(pred2)*100:.2f}%)")
    for c, p in zip(classes2, pred2): print(f"{c}: {p*100:.2f}%")
except Exception as e: print("m2 err:", e)

print("\n--- Testing problem_model_aug.h5 (128x128, cropped face) ---")
try:
    m3 = tf.keras.models.load_model('problem_model_aug.h5')
    img3 = cv2.cvtColor(cv2.resize(img_face, (128, 128)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    pred3 = m3.predict(np.expand_dims(img3, axis=0))[0]
    with open('problem_classes.pkl', 'rb') as f: classes3 = pickle.load(f)
    print(f"Top: {classes3[np.argmax(pred3)]} ({np.max(pred3)*100:.2f}%)")
    for c, p in zip(classes3, pred3): print(f"{c}: {p*100:.2f}%")
except Exception as e: print("m3 err:", e)
