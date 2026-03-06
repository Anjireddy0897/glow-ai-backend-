import os
import sqlite3
import pickle
import pymysql

# tensorflow is optional; catch missing package so app can start without AI
try:
    import tensorflow as tf
    # also bring in load_model function for later use
    from tensorflow.keras.models import load_model as _load_model
    load_model = _load_model
except ImportError:
    tf = None
    load_model = None
    print("[WARN] TensorFlow not installed; AI model endpoints will be disabled")

import json

pymysql.install_as_MySQLdb()

from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

# mail is optional; handling missing dependency
try:
    from flask_mail import Mail, Message
except ImportError:
    Mail = None
    Message = None
    print("[WARN] flask_mail not installed; email features will be disabled")


# Note: Flask was already imported above with additional helpers
from PIL import Image
import numpy as np

app = Flask(__name__)

# load primary model if TensorFlow is available
if load_model is not None:
    try:
        model = load_model("model.h5")
    except Exception as e:
        model = None
        print(f"[WARN] failed to load model.h5: {e}")
else:
    model = None

classes = ["acne", "blackheads", "darkspots", "pores", "wrinkles"]

# -----------------------------------
# CREATE FLASK APP
# -----------------------------------


# ================= CONFIG =================
app.config['SECRET_KEY'] = 'secretkey123'

# Database (MySQL already configured below)

# ================= MAIL CONFIG =================
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='kanjireddy2020@gmail.com',
    MAIL_PASSWORD= 'abviptkwfbyxnlmc' 
)

if Mail is not None:
    mail = Mail(app)
    print("MAIL SERVER:", app.config['MAIL_SERVER'])  # This is correct
else:
    mail = None
    print("[WARN] mail support disabled; flask_mail not available")

# TLS (587) is used above; if that fails try either of these instead:
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

import os
import cv2
import numpy as np
import random

UPLOAD_FOLDER = "uploads"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------
# FACE CROP (improves accuracy)
# ----------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def crop_face(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        return img_bgr  # if no face found, use full image

    # take largest face
    x, y, w, h = max(faces, key=lambda b: b[2]*b[3])

    # add margin
    pad = int(0.2 * w)
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(img_bgr.shape[1], x + w + pad)
    y2 = min(img_bgr.shape[0], y + h + pad)

    return img_bgr[y1:y2, x1:x2]

# -----------------------------------
# MYSQL CONFIG
# -----------------------------------

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'glow'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
if Mail is not None:
    mail = Mail(app)
else:
    mail = None

# -----------------------------------
# SQLITE DB FOR AI RECOMMENDATION
# -----------------------------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    skin_score INTEGER,
    product TEXT
)
""")

conn.commit()
conn.close()

# -----------------------------------
# LOAD AI MODEL (optional)
# -----------------------------------

if tf is not None:
    try:
        similarity = pickle.load(open('model.pkl', 'rb'))
        data = pickle.load(open('data.pkl', 'rb'))
    except Exception as e:
        similarity = None
        data = None
        print(f"[WARN] failed to load AI pickle models: {e}")

    # -----------------------------------
    # LOAD SKIN AI MODEL (IMAGE MODEL)
    # -----------------------------------
    try:
        skin_model = tf.keras.models.load_model("skin_model.h5")
        with open("classes.json", "r") as f:
            skin_classes = json.load(f)
        IMG_SIZE = 128
    except Exception as e:
        skin_model = None
        skin_classes = []
        IMG_SIZE = 0
        print(f"[WARN] failed to load skin model or classes: {e}")
else:
    similarity = None
    data = None
    skin_model = None
    skin_classes = []
    IMG_SIZE = 0

# -----------------------------------
# ROOT
# -----------------------------------

@app.route('/')
def home():
    return "SERVER WORKING OK"

# ================= FORGOT PASSWORD =================
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()

    # always return generic message to avoid user enumeration
    if not user:
        return jsonify({"message": "If email exists, reset link sent"})

    # generate dynamic link using url_for to respect host/port and use _external for full URL
    from flask import url_for
    reset_link = url_for('reset_password_page', email=email, _external=True)

    if mail is None:
        # mail subsystem disabled; log and return generic response
        print("[WARN] attempted to send reset email but mail is not configured")
        return jsonify({"message": "Reset link sent to email"})

    msg = Message(
        "Password Reset",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )

    msg.body = f"Click this link to reset your password:\n{reset_link}"
    mail.send(msg)

    return jsonify({"message": "Reset link sent to email"})

# ================= RESET PASSWORD PAGE =================
@app.route('/reset-password-page')
def reset_password_page():
    email = request.args.get('email')

    return render_template_string(f"""
        <h2>Reset Password</h2>
        <input type='password' id='new_password' placeholder='New Password'>
        <button onclick="resetPassword()">Update</button>

        <script>
        async function resetPassword() {{
            const new_password = document.getElementById('new_password').value;

            const response = await fetch('/reset-password', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    email: "{email}",
                    new_password: new_password
                }})
            }});

            const data = await response.json();
            alert(data.message);
        }}
        </script>
    """ )

# ================= RESET PASSWORD API =================
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        return jsonify({"message": "Invalid Email"})

    hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_pw, email))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Password Updated Successfully"})



# -----------------------------------
# REGISTER
# -----------------------------------

@app.route('/api/register/', methods=['POST'])
def register():

    data = request.json

    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirm_password')
    name = data.get('full_name')
    age = data.get('age')
    gender = data.get('gender')

    if password != confirm:
        return jsonify({
            "status": "error",
            "message": "Password mismatch"
        })

    cursor = mysql.connection.cursor()

    # 🔍 CHECK IF EMAIL EXISTS
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    existing = cursor.fetchone()

    if existing:
        return jsonify({
            "status": "error",
            "message": "Email already registered"
        })

    # 🔐 HASH PASSWORD
    hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

    cursor.execute("""
        INSERT INTO users (email,password,full_name,age,gender)
        VALUES (%s,%s,%s,%s,%s)
    """,(email,hash_password,name,age,gender))

    mysql.connection.commit()
    cursor.close()

    return jsonify({
        "status":"success",
        "message":"Registered successfully"
    })


# -----------------------------------
# LOGIN
# -----------------------------------

@app.route('/api/login/', methods=['POST'])

def login():

    data = request.json

    email = data['email']
    password = data['password']

    cursor = mysql.connection.cursor()

    cursor.execute("""

    SELECT id,password,full_name

    FROM users WHERE email=%s

    """,(email,))

    user = cursor.fetchone()

    cursor.close()

    if user:

        if bcrypt.check_password_hash(user[1],password):

            return jsonify({

                "status":"success",
                "user_id":user[0],
                "full_name":user[2]

            })

        else:

            return jsonify({

                "status":"error",
                "message":"Wrong password"

            })

    else:

        return jsonify({

            "status":"error",
            "message":"User not found"

        })


# -----------------------------------
# SUBMIT SURVEY
# -----------------------------------

@app.route('/api/submit_survey/', methods=['POST'])

def submit_survey():

    data = request.json

    user_id = data['user_id']
    skin_type = data['skin_type']
    concerns = ",".join(data['concerns'])
    sensitivity = data['sensitivity']
    climate = data['climate']
    ingredients = ",".join(data['ingredients'])
    allergies = ",".join(data['allergies'])

    score = 100

    if "Acne" in concerns:
        score -= 10

    if sensitivity == "High":
        score -= 5


    cursor = mysql.connection.cursor()

    cursor.execute("""

    INSERT INTO skin_surveys

    (user_id, skin_type, concerns, sensitivity, climate, ingredients, allergies, skin_score)

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)

    """,(user_id,skin_type,concerns,sensitivity,climate,ingredients,allergies,score))

    mysql.connection.commit()

    cursor.close()

    return jsonify({

        "status":"success",
        "skin_score":score

    })


# -----------------------------------
# UPLOAD API
# -----------------------------------

@app.route('/api/upload', methods=['POST'])
def upload():

    if 'image' not in request.files:

        return jsonify({
            "status": "error",
            "message": "No image uploaded"
        })

    user_id = request.form.get('user_id')

    if not user_id:

        return jsonify({
            "status":"error",
            "message":"user_id is required"
        })

    file = request.files['image']

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    file.save(filepath)


    img = cv2.imread(filepath)

    img = cv2.resize(img, (224,224))

    score = int(img.mean())


    if score > 130:

        skin_type = "Oily"
        product = "Niacinamide Cream"

    elif score > 80:

        skin_type = "Normal"
        product = "Vitamin C Cream"

    else:

        skin_type = "Dry"
        product = "Aloe Vera Gel"


    cursor = mysql.connection.cursor()

    cursor.execute("""
    INSERT INTO recommendation
    (user_id, product, skin_score, skin_type, status)
    VALUES (%s, %s, %s, %s, %s)
    """, (user_id, product, score, skin_type, "completed"))

    mysql.connection.commit()

    cursor.close()


    return jsonify({
        "status": "success",
        "skin_score": score,
        "skin_type": skin_type,
        "recommended_product": product
    })


# -----------------------------------
# AI RECOMMEND FUNCTION
# -----------------------------------

def ai_recommend():

    index = 0

    distances = similarity[index]

    products = sorted(list(enumerate(distances)),
                      reverse=True,
                      key=lambda x: x[1])[1:2]

    for i in products:

        return data.iloc[i[0]].product_name


# -----------------------------------
# RECOMMEND PRODUCT
# -----------------------------------

@app.route('/api/recommend_products/', methods=['POST'])

def recommend():

    data = request.json

    user_id = data['user_id']
    skin_score = data['skin_score']

    product = ai_recommend()

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO recommendations

    (user_id,product,skin_score)

    VALUES (?,?,?)

    """,(user_id,product,skin_score))

    conn.commit()

    conn.close()

    return jsonify({

        "status":"success",
        "recommended_product":product

    })


# -----------------------------------
# GET RECOMMENDATION
# -----------------------------------

def get_recommendation(label: str):
    rec = {
        "acne": {
            "product": "Anti-Acne Gel",
            "ingredients": ["Salicylic Acid", "Niacinamide"],
            "usage": "Apply at night on affected areas."
        },
        "pimple": {
            "product": "Spot Corrector Gel",
            "ingredients": ["Benzoyl Peroxide", "Tea Tree"],
            "usage": "Apply only on pimples 1–2 times/day."
        },
        "dry": {
            "product": "Hydrating Moisturizer",
            "ingredients": ["Hyaluronic Acid", "Ceramides"],
            "usage": "Apply morning and night."
        },
        "oily": {
            "product": "Oil-Control Moisturizer",
            "ingredients": ["Niacinamide", "Zinc"],
            "usage": "Apply twice daily."
        },
        "normal": {
            "product": "Daily Light Moisturizer",
            "ingredients": ["Aloe Vera", "Vitamin E"],
            "usage": "Apply once or twice daily."
        },
        "dark_circle": {
            "product": "Under-Eye Cream",
            "ingredients": ["Caffeine", "Vitamin C"],
            "usage": "Apply small amount under eyes at night."
        },
        "pigmentation": {
            "product": "Brightening Cream",
            "ingredients": ["Vitamin C", "Alpha Arbutin"],
            "usage": "Use at night + sunscreen in daytime."
        }
    }
    return rec.get(label, {
        "product": "General Moisturizer",
        "ingredients": ["Aloe Vera"],
        "usage": "Apply twice daily."
    })

@app.route('/api/get_recommendation/<int:user_id>', methods=['GET'])

def get_recommend(user_id):

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""

    SELECT product,skin_score

    FROM recommendations

    WHERE user_id=?

    ORDER BY id DESC LIMIT 1

    """,(user_id,))

    result = cursor.fetchone()

    conn.close()

    if result:

        return jsonify({

            "product":result[0],
            "skin_score":result[1]

        })

    else:

        return jsonify({

            "message":"No recommendation"

        })


# -----------------------------------
# AI IMAGE SKIN DETECTION

# helper utilities for improved recommendations
ISSUE_SET = {"acne", "pimple", "dark_circle", "pigmentation"}

def to_skin_type(label: str) -> str:
    if label in ["oil", "oily"]:
        return "oily"
    if label == "dry":
        return "dry"
    if label == "normal":
        return "normal"
    # if issue predicted -> infer
    if label in ["acne", "pimple"]:
        return "oily"
    if label == "dark_circle":
        return "dry"
    if label == "pigmentation":
        return "normal"
    return "normal"

def to_detected_issue(pred_vec, class_names, k=3):
    """
    Pick first ISSUE from top-k probabilities.
    This avoids always returning 'oil/dry/normal' as issue.
    """
    top_idx = np.argsort(pred_vec)[::-1][:k]
    for idx in top_idx:
        lbl = class_names[idx]
        if lbl in ISSUE_SET:
            return lbl
    return "none"

def final_recommendation(issue: str, skin_type: str) -> str:
    if issue == "acne":
        return "Use salicylic acid face wash + oil-free moisturizer"
    if issue == "pimple":
        return "Use niacinamide serum + pimple spot gel"
    if issue == "dark_circle":
        return "Use under-eye cream + sleep well"
    if issue == "pigmentation":
        return "Use oil-free Vitamin C cream + SPF sunscreen"

    # if no issue, recommend by skin type
    if skin_type == "oily":
        return "Use oil-control moisturizer + sunscreen"
    if skin_type == "dry":
        return "Use hydrating moisturizer + sunscreen"
    return "Use daily moisturizer + sunscreen"

# -----------------------------------

@app.route('/api/ai_skin_detect/', methods=['POST'])
def ai_skin_detect():

    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "user_id required"}), 400

    file = request.files['image']

    # ✅ READ IMAGE DIRECTLY (NO saving, prevents same-result bug)
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # debug info
    print("File:", file.filename, "Bytes:", len(file_bytes))

    if img is None:
        return jsonify({"status": "error", "message": "Invalid image"}), 400

    # ✅ face crop
    img_face = crop_face(img)

    # ✅ preprocess
    img_resized = cv2.resize(img_face, (IMG_SIZE, IMG_SIZE))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_rgb = img_rgb.astype(np.float32) / 255.0
    img_rgb = np.expand_dims(img_rgb, axis=0)

    # ✅ predict
    pred_vec = skin_model.predict(img_rgb)[0]
    top1_id = int(np.argmax(pred_vec))
    confidence = float(np.max(pred_vec)) * 100
    top1_label = skin_classes[top1_id]

    # debugging top3
    print("Top3:", sorted(list(zip(skin_classes, pred_vec)), key=lambda x: x[1], reverse=True)[:3])

    # ✅ required outputs
    skin_type = to_skin_type(top1_label)
    detected_issue = to_detected_issue(pred_vec, skin_classes, k=3)
    recommendation_text = final_recommendation(detected_issue, skin_type)

    # ✅ save into DB (optional)
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO recommendation (user_id, product, skin_score, skin_type, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, recommendation_text, int(confidence), skin_type, "completed"))
    mysql.connection.commit()
    cursor.close()

    # ✅ FINAL JSON (your requirement)
    return jsonify({
        "skin_type": skin_type,
        "detected_issue": detected_issue,
        "confidence": round(confidence, 2),
        "recommendation": recommendation_text
    })




# ai predection

# 🔥 Detect Skin Type
def detect_skin_type(issue):
    if issue in ["acne", "blackheads", "pores"]:
        return "oily"
    elif issue == "wrinkles":
        return "dry"
    else:
        return "normal"


# 🔥 Smart Recommendation Function
def get_recommendation(issue, skin_type):

    recommendations = {

        "acne": {
            "oily": [
                "Use Salicylic Acid face wash",
                "Apply oil-free moisturizer",
                "Use non-comedogenic sunscreen",
                "Avoid fried and oily foods"
            ],
            "normal": [
                "Use gentle cleanser",
                "Apply light moisturizer",
                "Use benzoyl peroxide spot treatment"
            ],
            "dry": [
                "Use hydrating cleanser",
                "Apply ceramide moisturizer",
                "Avoid over-washing face"
            ]
        },

        "blackheads": {
            "oily": [
                "Use clay mask twice weekly",
                "Salicylic acid serum",
                "Exfoliate 2 times per week"
            ],
            "normal": [
                "Gentle exfoliation",
                "Use pore tightening toner"
            ],
            "dry": [
                "Avoid harsh scrubs",
                "Use mild exfoliator",
                "Apply hydrating serum"
            ]
        },

        "darkspots": {
            "oily": [
                "Use Vitamin C serum",
                "Apply sunscreen daily",
                "Niacinamide serum"
            ],
            "normal": [
                "Vitamin C serum",
                "Use SPF 50 sunscreen",
                "Aloe vera gel"
            ],
            "dry": [
                "Hydrating Vitamin C serum",
                "Use moisturizer before treatment",
                "Avoid strong chemical peels"
            ]
        },

        "pores": {
            "oily": [
                "Use clay mask",
                "Niacinamide serum",
                "Oil control face wash"
            ],
            "normal": [
                "Mild exfoliation",
                "Pore tightening toner"
            ],
            "dry": [
                "Hydrating toner",
                "Avoid alcohol-based products"
            ]
        },

        "wrinkles": {
            "dry": [
                "Use Retinol at night",
                "Apply Hyaluronic Acid serum",
                "Use thick moisturizer",
                "Daily sunscreen SPF 50"
            ],
            "normal": [
                "Use anti-aging serum",
                "Vitamin C in morning",
                "Moisturizer + Sunscreen"
            ],
            "oily": [
                "Lightweight retinol",
                "Gel-based moisturizer",
                "Oil-free sunscreen"
            ]
        }
    }

    return recommendations.get(issue, {}).get(skin_type, ["Consult dermatologist"])


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["image"]
    image = Image.open(file).resize((224, 224))

    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)

    prediction = model.predict(image)
    class_index = np.argmax(prediction)
    confidence = round(float(prediction[0][class_index]) * 100, 2)
    issue = classes[class_index]
    skin_type = detect_skin_type(issue)
    recommendation = get_recommendation(issue, skin_type)

    return jsonify({
        "issue": issue,
        "skin_type": skin_type,
        "confidence": f"{confidence:.2f}%",
        "recommendation": recommendation
    })








# ---------------------------------------------------
# additional utility endpoint added by user request
# ---------------------------------------------------

def clamp(n, minn=0, maxn=100):
    """Keep score within [minn, maxn]."""
    return max(minn, min(maxn, n))


def calculate_skin_score(data):
    score = 100

    skin_type_penalty = {
        "normal": 0,
        "combination": 5,
        "oily": 10,
        "dry": 10,
        "sensitive": 15
    }
    skin_type = (data.get("skin_type") or "").lower()
    score -= skin_type_penalty.get(skin_type, 5)

    concern_penalty = {
        "acne": 12,
        "dark spots": 10,
        "wrinkles": 8,
        "dryness": 10,
        "oiliness": 8,
        "redness": 10,
        "large pores": 6,
        "uneven texture": 8,
        "dark circles": 6,
        "fine lines": 6
    }
    concerns = data.get("concerns") or []
    if isinstance(concerns, str):
        concerns = [c.strip() for c in concerns.split(",") if c.strip()]

    for c in concerns:
        score -= concern_penalty.get(c.lower(), 5)

    sensitivity_penalty = {
        "not sensitive": 0,
        "slightly sensitive": 5,
        "moderately sensitive": 10,
        "very sensitive": 18
    }
    sensitivity = (data.get("sensitivity") or "").lower()
    score -= sensitivity_penalty.get(sensitivity, 5)

    climate_penalty = {
        "temperate": 0,
        "humid": 3,
        "hot": 5,
        "dry": 8,
        "cold": 8
    }
    climate = (data.get("climate") or "").lower()
    score -= climate_penalty.get(climate, 3)

    restrictions = data.get("restrictions") or []
    if isinstance(restrictions, str):
        restrictions = [r.strip() for r in restrictions.split(",") if r.strip()]

    score -= min(len(restrictions) * 2, 12)

    return clamp(score)


@app.route("/skin-score", methods=["POST"])
def skin_score():
    data = request.get_json(force=True)
    score = calculate_skin_score(data)
    return jsonify({"skin_score": score}), 200


# -----------------------------------
# RUN
# -----------------------------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)