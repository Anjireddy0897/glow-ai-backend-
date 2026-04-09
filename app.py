import os
import re
import json
import pickle
import random
import numpy as np
import cv2
from PIL import Image
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Optional imports
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
except ImportError:
    tf = None
    load_model = None
    print("[WARN] TensorFlow not installed")

try:
    from flask_mail import Mail, Message
except ImportError:
    Mail = None
    Message = None
    print("[WARN] flask_mail not installed; email features will be disabled")

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://14.139.187.229:8073",
    "http://180.235.121.253:8149"
])

app.config['SECRET_KEY'] = 'secretkey123'

# ===============================
# LAZY LOAD MODELS (ON-DEMAND)
# ===============================

# Global model variables - load on first use, not at startup
model = None
classes = []
skin_model = None
issue_model = None
rec_model = None
le_skin = None
le_issue = None

def load_models():
    """Lazy-load all ML models on first use"""
    global model, classes, skin_model, issue_model, rec_model, le_skin, le_issue
    
    # Prevent reloading if already loaded
    if skin_model is not None and issue_model is not None:
        # Only check skin/issue models as primary requirements
        return
    
    print("[INFO] Loading ML models...")
    
    # 1. Load primary classification model (optional)
    if load_model is not None and model is None:
        try:
            model = load_model("problem_model_aug.h5")
            with open("problem_classes.pkl", "rb") as f:
                classes = pickle.load(f)
            print("[INFO] problem_model_aug.h5 loaded")
        except Exception as e:
            model = None
            classes = []
            print(f"[WARN] failed to load problem_model_aug.h5: {e}")
    
    # 2. Load Skin Type Model
    if skin_model is None:
        try:
            skin_model = tf.keras.models.load_model("skin_type_model.h5")
            print("[INFO] skin_type_model.h5 loaded successfully")
        except Exception as e:
            print(f"[WARN] Failed to load skin_type_model.h5: {e}")
            skin_model = None

    # 3. Load Issue Model
    if issue_model is None:
        try:
            issue_model = tf.keras.models.load_model("issues_model.h5")
            print("[INFO] issues_model.h5 loaded successfully")
        except Exception as e:
            print(f"[WARN] Failed to load issues_model.h5: {e}")
            issue_model = None

    # 4. Load Recommendation Model (depends on sklearn)
    if rec_model is None:
        try:
            with open("recommendation_model.pkl", "rb") as f:
                _rec_data = pickle.load(f)
            rec_model = _rec_data["model"]
            le_skin = _rec_data["skin_encoder"]
            le_issue = _rec_data["issue_encoder"]
            print("✅ Recommendation model and encoders loaded successfully")
        except Exception as e:
            rec_model = None
            le_skin = None
            le_issue = None
            print(f"[WARN] Failed to load recommendation model (might need sklearn): {e}")
    
    print("✅ Model loading routine completed.")

# ===============================
# CLASS LABELS
# ===============================

skin_classes = ['dry', 'normal', 'oil']

issue_classes = [
    'acne',
    'dark_circles',
    'pigmentation',
    'pores',
    'redness',
    'wrinkles'
]

IMG_SIZE = 224   # 🔥 IMPORTANT (must match your training)


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

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload-profile', methods=['POST'])
def upload_profile():
    if 'photo' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['photo']

    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(filepath)

    return jsonify({
        "filename": filename,
        "image_url": request.host_url + 'static/uploads/' + filename
    })

@app.route('/get-profile/<filename>', methods=['GET'])
def get_profile(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ----------------------------
# PASSWORD VALIDATION
# ----------------------------

def validate_full_name(name):
    if not name:
        return "Full name is required"
    if len(name) < 2:
        return "Full name must be at least 2 characters"
    if not re.match(r'^[A-Za-z ]+$', name):
        return "Full name must contain only alphabets"
    return None


def validate_age(age):
    if not age:
        return "Age is required"
    if not str(age).isdigit():
        return "Age must be a number"
    age = int(age)
    if age < 0:
        return "Age cannot be negative"
    return None


def validate_gender(gender):
    if not gender:
        return "Gender is required"
    if gender.strip().title() not in ["Male", "Female", "Other"]:
        return "Please select a valid gender (Male, Female, or Other)"
    return None


def validate_email(email):
    if not email:
        return "Email is required"
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return "Invalid email format"
    return None


def validate_password(password):
    if len(password) < 3:
        return "Password must be at least 3 characters"
    return None


def validate_confirm_password(password, confirm_password):
    if password != confirm_password:
        return "Passwords do not match"
    return None


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
# DATABASE CONFIG (MySQL)
# -----------------------------------

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 3306   # 🔥 MUST MATCH XAMPP
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'antireddy'

mysql = MySQL(app)

print(f"[INFO] MySQL Config: {app.config['MYSQL_HOST']} - {app.config['MYSQL_USER']} - {app.config['MYSQL_DB']}")

bcrypt = Bcrypt(app)
if Mail is not None:
    mail = Mail(app)
else:
    mail = None

# -----------------------------------
# LOAD RECOMMENDER SIMILARITY MODEL (optional)
# -----------------------------------

if tf is not None:
    try:
        similarity = pickle.load(open('model.pkl', 'rb'))
        _sim_data = pickle.load(open('data.pkl', 'rb'))
    except Exception as e:
        similarity = None
        _sim_data = None
        print(f"[WARN] failed to load similarity pickle models: {e}")
else:
    similarity = None
    _sim_data = None

# -----------------------------------
# ROOT
# -----------------------------------

@app.route('/')
def home():
    return "SERVER WORKING OK"

# -----------------------------------
# SIMPLE CAMERA PAGE (opens webcam)
# -----------------------------------
# Clicking the button triggers getUserMedia which requests camera
# access from the browser.  Note that this only works over HTTPS or
# on localhost; mobile devices may require the <input> trick instead.
# If you already have a button in some template, mimic the JS below
# or point the button href to "/camera".

@app.route('/camera')
def camera_page():
    return render_template_string("""
        <h2>Camera Test</h2>
        <button id="openCameraBtn">Open Camera</button>
        <video id="video" width="640" height="480" autoplay></video>
        <script>
        const btn = document.getElementById('openCameraBtn');
        btn.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                document.getElementById('video').srcObject = stream;
            } catch (err) {
                alert('Unable to access camera: ' + err.message);
            }
        });
        </script>
    """)

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

@app.route('/api/register', methods=['POST'])
@app.route('/api/register/', methods=['POST'])
def register():
    try:
        data = request.json or {}

        full_name = data.get('full_name', '').strip()
        age = str(data.get('age', '')).strip()
        gender = data.get('gender', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        errors = {}

        # VALIDATIONS
        if validate_full_name(full_name):
            errors['full_name'] = validate_full_name(full_name)

        if validate_age(age):
            errors['age'] = validate_age(age)

        if validate_gender(gender):
            errors['gender'] = validate_gender(gender)

        if validate_email(email):
            errors['email'] = validate_email(email)

        if validate_password(password):
            errors['password'] = validate_password(password)

        if validate_confirm_password(password, confirm_password):
            errors['confirm_password'] = validate_confirm_password(password, confirm_password)

        if errors:
            return jsonify({"status": "error", "errors": errors}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE()")
        print("[DEBUG] Current DB:", cursor.fetchone())

        cursor.execute("SELECT COUNT(*) FROM users")
        print("[DEBUG] Total users in DB:", cursor.fetchone())
        # ✅ FIXED CHECK (DIRECT SQL)
        cursor.execute("SELECT id FROM users WHERE LOWER(email)=%s", (email,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 400

        # HASH PASSWORD
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # INSERT USER
        cursor.execute("""
            INSERT INTO users (email, password, full_name, age, gender)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, hashed_pw, full_name, age, gender))

        mysql.connection.commit()
        user_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# -----------------------------------
# LOGIN
# -----------------------------------

@app.route('/api/login', methods=['POST'])
@app.route('/api/login/', methods=['POST'])
def login():

    data = request.json or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"})

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id,password,full_name FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            user_id, user_password, full_name = user
            if bcrypt.check_password_hash(user_password, password):
                return jsonify({
                    "status": "success",
                    "user_id": user_id,
                    "id": user_id,
                    "full_name": full_name,
                    "email": email,
                    "user": {
                        "id": user_id,
                        "user_id": user_id,
                        "full_name": full_name
                    }
                })
            else:
                return jsonify({"status": "error", "message": "Wrong password"})
        else:
            return jsonify({"status": "error", "message": "User not found"})
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500


# -----------------------------------
# INITIALIZE DATABASE TABLES
# -----------------------------------
def init_db():
    print(f"[INFO] Initializing MySQL database: facecream...")
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                age VARCHAR(10),
                gender VARCHAR(50)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS skin_surveys (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                skin_type VARCHAR(100),
                concerns TEXT,
                sensitivity VARCHAR(100),
                climate VARCHAR(100),
                ingredients TEXT,
                allergies TEXT,
                skin_score INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                product VARCHAR(255),
                skin_score DECIMAL(10, 2),
                skin_type VARCHAR(100),
                status VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                skin_type VARCHAR(100),
                issue VARCHAR(100),
                confidence FLOAT,
                skin_score INT,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Auto-migrate: Add skin_score column if the user created the table without it previously
            try:
                cursor.execute("ALTER TABLE ai_results ADD COLUMN skin_score INT;")
                print("[INFO] Migrated ai_results table to include skin_score.")
            except Exception as migrate_err:
                # Normal if column already exists
                pass

            mysql.connection.commit()
            cursor.close()
            print(f"[INFO] Database tables verified/created successfully.")
    except Exception as e:
        print("[WARN] Could not initialize database tables:", e)

# Run initialization before the first request
@app.before_request
def setup_tables():
    if not hasattr(app, 'tables_initialized'):
        init_db()
        app.tables_initialized = True

# -----------------------------------
# SUBMIT SURVEY
# -----------------------------------

@app.route('/api/submit_survey', methods=['POST'])
@app.route('/api/submit_survey/', methods=['POST'])
def submit_survey():
    data = request.json

    user_id = data.get('user_id')
    skin_type = data.get('skin_type', '')
    concerns = data.get('concerns', [])
    sensitivity = data.get('sensitivity', '')
    climate = data.get('climate', '')
    ingredients = data.get('ingredients', [])
    allergies = data.get('allergies', [])

    score = calculate_skin_score(data)

    print("🔥 NEW FUNCTION RUNNING")
    print("SCORE:", score)

    return jsonify({"test": "NEW API WORKING"})


# -----------------------------------
# GET LATEST SURVEY (for home screen display)
# -----------------------------------

@app.route('/api/get_latest_survey/<int:user_id>', methods=['GET'])
def get_latest_survey(user_id):
    """
    Fetch the most recent survey with full details and score.
    Used to display survey results on home screen after completion.
    """
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                skin_type,
                concerns,
                sensitivity,
                climate,
                ingredients,
                allergies,
                skin_score,
                created_at
            FROM skin_surveys 
            WHERE user_id=%s 
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return jsonify({
                "status": "error",
                "message": "No survey found for this user",
                "data": None
            }), 404
        
        # Format the response
        return jsonify({
            "status": "success",
            "data": {
                "survey_id": result[0],
                "skin_type": result[1] or "Not specified",
                "concerns": result[2].split(',') if result[2] else [],
                "sensitivity": result[3] or "Not specified",
                "climate": result[4] or "Not specified",
                "ingredients": result[5].split(',') if result[5] else [],
                "allergies": result[6].split(',') if result[6] else [],
                "skin_score": result[7] or 0,
                "score_rating": get_score_rating(result[7] or 0),
                "created_at": result[8].strftime("%Y-%m-%d %H:%M:%S") if hasattr(result[8], 'strftime') else str(result[8])
            }
        })
    except Exception as e:
        print(f"[ERROR] get_latest_survey failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------------
# HOME SCREEN DATA (combined user + latest analysis)
# -----------------------------------

@app.route('/api/get_home_screen/<int:user_id>', methods=['GET'])
def get_home_screen(user_id):
    """
    Fetch combined data for home screen including:
    - User profile info
    - Latest survey score
    - Total analyses count
    - Latest score and date
    """
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT id, full_name, email, age, gender
            FROM users
            WHERE id=%s
        """, (user_id,))
        user_result = cursor.fetchone()
        
        if not user_result:
            cursor.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404
        
        # Get latest survey
        cursor.execute("SELECT skin_score, created_at, 'Survey' as type FROM skin_surveys WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (user_id,))
        latest_survey = cursor.fetchone()
        
        # Get latest scan from ai_results table
        cursor.execute("""
            SELECT skin_score, created_at, 'Scan' as type, recommendation as product 
            FROM ai_results 
            WHERE user_id=%s 
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        latest_scan = cursor.fetchone()
        
        # Determine the truly latest analysis
        latest_analysis = None
        if latest_survey and latest_scan:
            # compare dates
            if latest_survey[1] >= latest_scan[1]:
                latest_analysis = list(latest_survey) + [None] 
            else:
                latest_analysis = latest_scan
        elif latest_survey:
            latest_analysis = list(latest_survey) + [None]
        elif latest_scan:
            latest_analysis = latest_scan
            
        # Get total analyses count
        cursor.execute("""
            SELECT COUNT(*) FROM skin_surveys WHERE user_id=%s
        """, (user_id,))
        survey_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM ai_results WHERE user_id=%s
        """, (user_id,))
        scan_count = cursor.fetchone()[0]
        
        cursor.close()
        
        # Prepare response
        response_data = {
            "status": "success",
            "user": {
                "id": user_result[0],
                "name": user_result[1] or "User",
                "email": user_result[2] or "N/A",
                "age": str(user_result[3]) if user_result[3] is not None else "",
                "gender": str(user_result[4]) if user_result[4] is not None else ""
            },
            "analytics": {
                "total_surveys": survey_count,
                "total_scans": scan_count,
                "total_analyses": survey_count + scan_count
            },
            "latest_survey": None,
            "latest_analysis": None
        }
        
        if latest_analysis:
            response_data["latest_analysis"] = {
                "score": int(latest_analysis[0]) if latest_analysis[0] else 0,
                "score_rating": get_score_rating(latest_analysis[0] or 0),
                "type": latest_analysis[2],
                "date": latest_analysis[1].strftime("%d/%m/%Y") if hasattr(latest_analysis[1], 'strftime') else str(latest_analysis[1]),
                "product": latest_analysis[3] if len(latest_analysis) > 3 else None
            }
            # For backward compatibility with existing frontend
            response_data["latest_survey"] = response_data["latest_analysis"]
        
        return jsonify(response_data)
    except Exception as e:
        print(f"[ERROR] get_home_screen failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------------
# HELPER: Score rating function
# -----------------------------------

def get_score_rating(score):
    """
    Convert numerical score (0-100) to a rating category.
    """
    score = int(score) if score else 0
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Needs Care"


# -----------------------------------
# UPDATE PROFILE
# -----------------------------------

@app.route('/api/update_profile', methods=['POST'])
@app.route('/api/update_profile/', methods=['POST'])
def update_profile():
    data = request.json
    user_id = data.get('user_id')
    full_name = data.get('full_name')
    email = data.get('email')
    age = data.get('age')
    gender = data.get('gender')

    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE users SET full_name=%s, email=%s, age=%s, gender=%s WHERE id=%s
        """, (full_name, email, age, gender, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"status": "success", "message": "Profile updated successfully"})
    except Exception as e:
        print(f"[ERROR] update_profile failed: {e}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


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

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
        INSERT INTO recommendation
        (user_id, product, skin_score, skin_type, status)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_id, product, score, skin_type, "completed"))

        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print("[WARN] Could not save upload recommendation:", e)


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
    if _sim_data is None:
        return "General Moisturizer"
    index = 0
    distances = similarity[index]
    products = sorted(list(enumerate(distances)),
                      reverse=True,
                      key=lambda x: x[1])[1:2]
    for i in products:
        return _sim_data.iloc[i[0]].product_name
    return "General Moisturizer"


# -----------------------------------
# RECOMMEND PRODUCT
# -----------------------------------

@app.route('/api/recommend_products', methods=['POST'])
@app.route('/api/recommend_products/', methods=['POST'])

def recommend():

    data = request.json

    user_id = data['user_id']
    skin_score = data['skin_score']

    product = ai_recommend() if similarity is not None else "General Moisturizer"

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
        INSERT INTO recommendation (user_id, product, skin_score, skin_type, status)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_id, product, skin_score, "Unknown", "completed"))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print("[WARN] Could not save recommender product:", e)

    return jsonify({
        "status":"success",
        "recommended_product":product
    })


# -----------------------------------
# GET RECOMMENDATION (FOR DASHBOARD)
# -----------------------------------

@app.route('/api/get_recommendation/<int:user_id>', methods=['GET'])
def get_recommend(user_id):
    """
    Fetches the most recent skin score/analysis from either the 
    camera scans (recommendation table) or surveys (skin_surveys table).
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Check latest camera scan from ai_results
        cursor.execute("""
            SELECT skin_score, skin_type, created_at
            FROM ai_results 
            WHERE user_id=%s 
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        scan_result = cursor.fetchone()

        # Check latest survey
        cursor.execute("""
            SELECT skin_score, skin_type, created_at
            FROM skin_surveys 
            WHERE user_id=%s 
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        survey_result = cursor.fetchone()
        
        cursor.close()

        latest = None
        latest_source = None
        if scan_result and survey_result:
            # Compare timestamps (idx 2)
            if scan_result[2] > survey_result[2]:
                latest = scan_result
                latest_source = 'scan'
            else:
                latest = survey_result
                latest_source = 'survey'
        elif scan_result:
            latest = scan_result
            latest_source = 'scan'
        elif survey_result:
            latest = survey_result
            latest_source = 'survey'

        if latest:
            return jsonify({
                "status": "success",
                "skin_score": latest[0] or 0,
                "skin_type": latest[1] or "Unknown",
                "source": latest_source
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No recommendation found"
            })
    except Exception as e:
        print(f"[ERROR] get_recommendation failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# -----------------------------------
# DASHBOARD STATS
# -----------------------------------

@app.route('/api/get_dashboard_stats/<int:user_id>', methods=['GET'])
def get_dashboard_stats(user_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Count total scans from ai_results
        cursor.execute("SELECT COUNT(*) FROM ai_results WHERE user_id=%s", (user_id,))
        scan_count = cursor.fetchone()[0]
        
        # Count total surveys
        cursor.execute("SELECT COUNT(*) FROM skin_surveys WHERE user_id=%s", (user_id,))
        survey_count = cursor.fetchone()[0]
        
        total_analyses = scan_count + survey_count
        
        # Get latest records to find the most recent score and date from ai_results
        cursor.execute("SELECT skin_score, created_at FROM ai_results WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
        latest_scan = cursor.fetchone()
        
        cursor.execute("SELECT skin_score, created_at FROM skin_surveys WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
        latest_survey = cursor.fetchone()
        
        cursor.close()
        
        latest_score = 0
        latest_date = "No Analysis"
        
        results = []
        if latest_scan:
            results.append({"score": latest_scan[0], "date": latest_scan[1]})
        if latest_survey:
            results.append({"score": latest_survey[0], "date": latest_survey[1]})
            
        if results:
            # Sort by date descending
            results.sort(key=lambda x: x["date"], reverse=True)
            latest_score = results[0]["score"]
            latest_date = results[0]["date"].strftime("%d/%m/%Y") if hasattr(results[0]["date"], 'strftime') else str(results[0]["date"])
            
        return jsonify({
            "status": "success",
            "total_analyses": total_analyses,
            "latest_score": latest_score,
            "latest_date": latest_date
        })
    except Exception as e:
        print(f"[ERROR] get_dashboard_stats failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------------
# GET ALL ANALYSES (FOR HISTORY/DASHBOARD)
# -----------------------------------

@app.route('/api/get_all_recommendations/<int:user_id>', methods=['GET'])
def get_all_recommendations(user_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Get all scans from ai_results (full detail)
        cursor.execute("""
            SELECT id, user_id, skin_type, issue, confidence, recommendation, created_at, skin_score
            FROM ai_results 
            WHERE user_id=%s 
            ORDER BY created_at DESC
        """, (user_id,))
        scans = cursor.fetchall()

        # Get all surveys
        cursor.execute("""
            SELECT id, user_id, skin_type, concerns, sensitivity, climate, ingredients, allergies, skin_score, created_at
            FROM skin_surveys 
            WHERE user_id=%s 
            ORDER BY created_at DESC
        """, (user_id,))
        surveys = cursor.fetchall()
        
        cursor.close()

        all_results = []
        for s in scans:
            all_results.append({
                "id": s[0],
                "user_id": s[1],
                "skin_type": s[2],
                "issue": s[3],
                "confidence": float(s[4]) if s[4] is not None else 0.0,
                "recommendation": s[5],
                "created_at": s[6].strftime("%Y-%m-%d %H:%M:%S") if hasattr(s[6], 'strftime') else str(s[6]),
                "raw_date": s[6],
                "skin_score": s[7] or 0,
                "source": "scan"
            })
        for s in surveys:
            all_results.append({
                "id": s[0],
                "user_id": s[1],
                "skin_type": s[2],
                "concerns": s[3],
                "sensitivity": s[4],
                "climate": s[5],
                "ingredients": s[6],
                "allergies": s[7],
                "skin_score": s[8] or 0,
                "created_at": s[9].strftime("%Y-%m-%d %H:%M:%S") if hasattr(s[9], 'strftime') else str(s[9]),
                "raw_date": s[9],
                "source": "survey"
            })

        # Sort by raw date descending
        all_results.sort(key=lambda x: x["raw_date"], reverse=True)
        
        # Remove raw_date before sending
        for r in all_results:
            del r["raw_date"]

        return jsonify({
            "status": "success",
            "results": all_results
        })
    except Exception as e:
        print(f"[ERROR] get_all_recommendations failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


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

# =====================================================
# HELPER: rule-based skin analysis (fallback when no AI)
# =====================================================
def rule_based_skin_analysis(img_bgr):
    """
    Analyze skin using OpenCV heuristics when TensorFlow model
    is not available.  Returns a dict with comprehensive analysis.
    """
    face = crop_face(img_bgr)
    hsv = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)

    avg_brightness = float(hsv[:, :, 2].mean())
    avg_saturation = float(hsv[:, :, 1].mean())
    brightness_std = float(hsv[:, :, 2].std())
    avg_L = float(lab[:, :, 0].mean())

    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

    dark_thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)[1]
    dark_ratio = float(dark_thresh.sum()) / (dark_thresh.shape[0] * dark_thresh.shape[1] * 255)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    bright_thresh = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY)[1]
    bright_ratio = float(bright_thresh.sum()) / (bright_thresh.shape[0] * bright_thresh.shape[1] * 255)

    edges = cv2.Canny(gray, 40, 120)
    edge_ratio = float(edges.sum()) / (edges.shape[0] * edges.shape[1] * 255)

    local_std = cv2.GaussianBlur(gray.astype(np.float32), (15, 15), 0)
    local_sq = cv2.GaussianBlur((gray.astype(np.float32))**2, (15, 15), 0)
    texture_var = float(np.sqrt(np.maximum(local_sq - local_std**2, 0)).mean())

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    pore_score = float(tophat.mean())

    if avg_brightness > 140 and avg_saturation > 60:
        skin_type = "oily"
        oil_level = min(int((avg_saturation / 180) * 100), 100)
        hydration_level = max(40, 70 - int(avg_saturation * 0.3))
    elif avg_brightness < 110 and avg_saturation < 60:
        skin_type = "dry"
        oil_level = max(10, int((avg_saturation / 180) * 50))
        hydration_level = max(20, 50 - int(brightness_std * 0.5))
    elif avg_saturation > 40 and avg_saturation < 80:
        skin_type = "combination"
        oil_level = int((avg_saturation / 180) * 70)
        hydration_level = 55
    else:
        skin_type = "normal"
        oil_level = int((avg_saturation / 180) * 60)
        hydration_level = 65

    issues_found = []
    if dark_ratio > 0.05:
        issues_found.append(("dark spots", 62 + min(dark_ratio * 200, 23)))
    if bright_ratio > 0.03:
        issues_found.append(("acne", 60 + min(bright_ratio * 300, 25)))
    if edge_ratio > 0.06:
        issues_found.append(("wrinkles", 58 + min(edge_ratio * 150, 22)))
    if pore_score > 8:
        issues_found.append(("pores", 55 + min(pore_score * 2, 20)))
    if texture_var > 20:
        issues_found.append(("uneven texture", 55 + min(texture_var, 20)))
    if dark_ratio > 0.03 and avg_L < 120:
        issues_found.append(("pigmentation", 58 + min(dark_ratio * 150, 20)))

    if not issues_found:
        if skin_type == "oily":
            issues_found.append(("excess oil", 65.0))
        elif skin_type == "dry":
            issues_found.append(("dryness", 65.0))
        else:
            issues_found.append(("mild unevenness", 55.0))

    issues_found.sort(key=lambda x: x[1], reverse=True)
    detected_issue = issues_found[0][0]
    confidence = min(issues_found[0][1], 88.0)

    # Score calculation
    skin_score = 100
    skin_score -= min(int(dark_ratio * 150), 25) # Slightly more weight but reasonable
    skin_score -= min(int(bright_ratio * 200), 20)
    skin_score -= min(int(edge_ratio * 100), 20)
    skin_score -= min(int(pore_score * 0.8), 15)
    skin_score -= min(int(texture_var * 0.4), 15)
    
    # Type adjustments
    if skin_type == "oily": skin_score -= 5
    elif skin_type == "dry": skin_score -= 8
    
    # Ensure a healthier floor for no major issues detected
    if not issues_found or (len(issues_found) == 1 and issues_found[0][0] in ["mild unevenness", "none"]):
        skin_score = max(75, skin_score)
    else:
        skin_score = max(40, min(skin_score, 100))

    tips = []
    if skin_type == "oily":
        tips.append("Use an oil-free, gel-based cleanser")
        tips.append("Apply lightweight moisturizer")
    elif skin_type == "dry":
        tips.append("Use hydrating cream-based cleanser")
        tips.append("Apply rich moisturizer with ceramides")
    else:
        tips.append("Use gentle balanced cleanser")
        tips.append("Apply lightweight daily moisturizer")

    for issue_name, _ in issues_found[:3]:
        if "acne" in issue_name:
            tips.append("Use salicylic acid spot treatment")
        elif "dark" in issue_name or "pigmentation" in issue_name:
            tips.append("Apply Vitamin C serum")
        elif "wrinkle" in issue_name or "fine lines" in issue_name:
            tips.append("Use retinol serum at night")
        elif "pore" in issue_name:
            tips.append("Use niacinamide serum")
        elif "uneven" in issue_name:
            tips.append("Exfoliate gently 2 times per week")

    tips.append("Always apply sunscreen SPF 30+ daily")
    
    unique_tips = []
    for t in tips:
        if t not in unique_tips: unique_tips.append(t)
    tips = unique_tips[:5]

    return {
        "skin_type": skin_type,
        "detected_issue": detected_issue,
        "confidence": confidence,
        "skin_score": skin_score,
        "oil_level": oil_level,
        "hydration_level": hydration_level,
        "issues": [{"name": n, "confidence": round(c, 1)} for n, c in issues_found[:4]],
        "tips": tips
    }

# -----------------------------------

@app.route('/api/ai_skin_detect/', methods=['POST'])
def ai_skin_detect():
    load_models()  # Lazy-load models on first use
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"}), 400

    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "user_id required"}), 400

    file = request.files['image']

    # READ IMAGE DIRECTLY
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"status": "error", "message": "Invalid image"}), 400

    # try AI prediction FIRST, if skin_model is loaded
    if skin_model is not None and issue_model is not None:
        try:
            img_face = crop_face(img)
            img_resized = cv2.resize(img_face, (IMG_SIZE, IMG_SIZE))
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            img_normalized = img_rgb.astype(np.float32) / 255.0
            img_arr = np.expand_dims(img_normalized, axis=0)

            # 1. Detect Skin Type
            skin_pred = skin_model.predict(img_arr)[0]
            skin_id = int(np.argmax(skin_pred))
            skin_type = skin_classes[skin_id]
            skin_confidence = float(np.max(skin_pred)) * 100

            # 2. Detect Issue
            issue_pred = issue_model.predict(img_arr)[0]
            issue_id = int(np.argmax(issue_pred))
            detected_issue = issue_classes[issue_id]
            issue_confidence = float(np.max(issue_pred)) * 100
            
            # Rule-based analysis for tips and score
            rule_results = rule_based_skin_analysis(img)
            
            # Smart recommendation
            recommendations = get_recommendation_by_issue(detected_issue, skin_type)
            if isinstance(recommendations, list):
                main_rec = recommendations[0] if recommendations else "Maintain current routine"
                tips = recommendations
            else:
                main_rec = recommendations
                tips = rule_results["tips"]

            # Merge results
            final_results = {
                "skin_type": skin_type.capitalize(),
                "detected_issue": detected_issue.capitalize() if detected_issue != "none" else "Normal",
                "confidence": round(max(skin_confidence, issue_confidence), 2),
                "skin_score": rule_results["skin_score"],
                "oil_level": rule_results["oil_level"],
                "hydration_level": rule_results["hydration_level"],
                "recommendation": main_rec,
                "issues": [{"name": detected_issue, "confidence": round(issue_confidence, 1)}],
                "tips": tips if tips else rule_results["tips"]
            }
        except Exception as e:
            print(f"[WARN] AI model failed during prediction: {e}. Falling back to rule-based.")
            final_results = rule_based_skin_analysis(img)
    else:
        # Fallback to pure rule-based
        print("[INFO] AI model not loaded. Using rule-based analysis.")
        final_results = rule_based_skin_analysis(img)

    try:
        # save into DB using MySQL
        cursor = mysql.connection.cursor()
        # save into ai_results table as requested
        actual_score = int(final_results.get("skin_score", 60))
        issue = final_results.get("detected_issue", "Normal")
        conf = final_results.get("confidence", 0.0)
        rec = final_results.get("recommendation", "See Tips")

        cursor.execute("""
            INSERT INTO ai_results (user_id, skin_type, issue, confidence, skin_score, recommendation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, final_results["skin_type"], issue, conf, actual_score, rec))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print("[WARN] Could not save recommendation to DB:", e)

    return jsonify(final_results)


# ai predection

# 🔥 Detect Skin Type
def detect_skin_type(issue):
    if issue in ["acne", "blackheads", "pores", "pimple"]:
        return "oily"
    elif issue in ["wrinkles", "dark_circle"]:
        return "dry"
    else:
        return "normal"


# 🔥 Smart Recommendation Function
def get_recommendation_by_issue(issue, skin_type):

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
        },

        "pimple": {
            "oily": [
                "Use Salicylic Acid face wash",
                "Apply oil-free moisturizer",
                "Use benzoyl peroxide spot treatment",
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
                "Use pimple patches"
            ]
        },

        "dark_circle": {
            "oily": [
                "Use caffeine eye serum",
                "Get at least 8 hours of sleep",
                "Wear sunglasses outdoors"
            ],
            "normal": [
                "Apply hydrating eye cream",
                "Use cold compress in the morning",
                "Get adequate rest"
            ],
            "dry": [
                "Use thick hydrating eye cream",
                "Apply hyaluronic acid serum under eyes",
                "Drink more water"
            ]
        },

        "pigmentation": {
            "oily": [
                "Use niacinamide serum",
                "Apply broad-spectrum sunscreen",
                "Exfoliate with BHA weekly"
            ],
            "normal": [
                "Use Vitamin C serum daily",
                "Always apply SPF 50 sunscreen",
                "Use gentle alpha arbutin serum"
            ],
            "dry": [
                "Apply hydrating Vitamin C serum",
                "Use thick moisturizer to repair barrier",
                "Wear sunscreen every day"
            ]
        }
    }

    return recommendations.get(issue, {}).get(skin_type, ["Consult dermatologist"])


@app.route("/ai-final", methods=["POST"])
def ai_final():
    load_models()  # Lazy-load models on first use

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']

    # Read image
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image"}), 400

    # ===============================
    # SKIN & ISSUE DETECTION (AI with Rule-based Fallback)
    # ===============================
    
    # Initialize variables with defaults
    skin_result = "normal"
    issue_result = "none"
    confidence = 0.0
    
    # Try AI FIRST if models are loaded
    if skin_model is not None and issue_model is not None:
        try:
            # Preprocess
            img_resized = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            img_arr = img_rgb.astype(np.float32) / 255.0
            img_arr = np.expand_dims(img_arr, axis=0)

            # Skin Type Detection
            skin_pred = skin_model.predict(img_arr)
            skin_id = int(np.argmax(skin_pred))
            skin_result = skin_classes[skin_id]
            confidence = float(np.max(skin_pred)) * 100

            # Issue Detection
            issue_pred = issue_model.predict(img_arr)
            issue_id = int(np.argmax(issue_pred))
            issue_result = issue_classes[issue_id]
            print(f"[INFO] AI Prediction Success: {skin_result}, {issue_result}")
            
        except Exception as ai_err:
            print(f"[WARN] AI Prediction failed: {ai_err}. Falling back to rule-based.")
            # We'll use the rule-based results below
            rule_results = rule_based_skin_analysis(img)
            skin_result = rule_results.get("skin_type", "normal")
            issue_result = rule_results.get("detected_issue", "none")
            confidence = rule_results.get("confidence", 70.0)
    else:
        print("[INFO] AI models not loaded. Using rule-based analysis fallback.")
        rule_results = rule_based_skin_analysis(img)
        skin_result = rule_results.get("skin_type", "normal")
        issue_result = rule_results.get("detected_issue", "none")
        confidence = rule_results.get("confidence", 70.0)

    # ===============================
    # RECOMMENDATION
    # ===============================
    recommendation = "Consult dermatologist"
    try:
        if rec_model is not None and le_skin is not None and le_issue is not None:
            skin_encoded = le_skin.transform([skin_result])[0]
            issue_encoded = le_issue.transform([issue_result])[0]
            rec = rec_model.predict([[skin_encoded, issue_encoded]])
            recommendation = str(rec[0])
    except Exception as rec_err:
        print(f"[WARN] Recommendation model failed: {rec_err}")

    # ===============================
    # FINAL RESPONSE & DB SAVE
    # ===============================
    print(f"[INFO] Entering DB Save section for /ai-final")

    # Get skin score
    try:
        rule_results = rule_based_skin_analysis(img)
        skin_score = rule_results.get("skin_score", 80)
        print(f"[INFO] Calculated skin_score: {skin_score}")
    except Exception as e:
        print(f"[WARN] Error calculating score: {e}")
        skin_score = max(40, min(int(confidence), 100))  # fallback
        print(f"[INFO] Fallback skin_score: {skin_score}")

    # Robust User ID retrieval
    user_id = (
        request.form.get('user_id') or 
        request.form.get('id') or
        request.form.get('userId') or
        request.form.get('uid') or
        request.args.get('user_id') or
        request.args.get('id')
    )
    
    # Check JSON if available
    if not user_id and request.is_json:
        user_id = request.json.get('user_id') or request.json.get('id')
    
    save_status = "Not attempted (Missing user_id)"
    
    # ✅ SAVE IN ai_results TABLE
    if user_id:
        print(f"[INFO] Attempting to save results for user_id: {user_id}")
        try:
            cursor = mysql.connection.cursor()

            query = """
                INSERT INTO ai_results 
                (user_id, skin_type, issue, confidence, skin_score, recommendation)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                user_id,
                skin_result,
                issue_result,
                float(confidence),
                int(skin_score),
                recommendation
            )
            
            print(f"[DEBUG] Executing Query: {query}")
            print(f"[DEBUG] With Params: {params}")

            cursor.execute(query, params)
            mysql.connection.commit()
            
            # Verify row count
            if cursor.rowcount > 0:
                save_status = "Successfully saved to ai_results"
                print(f"[SUCCESS] AI result saved in ai_results table for user {user_id}")
            else:
                save_status = "Failed: Row count was 0"
                print(f"[WARN] No rows were affected in ai_results save")
                
            cursor.close()

        except Exception as db_err:
            save_status = f"Error: {str(db_err)}"
            print(f"[ERROR] CRITICAL DB ERROR: {db_err}")
    else:
        print(f"[WARN] Skipping DB save: user_id could not be found in form, args, or JSON.")

    return jsonify({
        "status": "success",
        "Skin Type": skin_result,
        "Issue": issue_result,
        "Confidence": f"{confidence:.2f}%",
        "Recommendation": recommendation,
        "skin_score": skin_score,
        "user_id_received": user_id,
        "db_save_status": save_status
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    return ai_final()


# Temporary debug route (STEP 2)
@app.route("/ai-final-debug", methods=["POST"])
def ai_final_debug():
    return jsonify({"message": "API WORKING"})


# ---------------------------------------------------
# additional utility endpoint added by user request
# ---------------------------------------------------

def clamp(n, minn=0, maxn=100):
    """Keep score within [minn, maxn]."""
    return max(minn, min(maxn, n))


def calculate_skin_score(data):
    score = 0

    # -------------------------
    # 1. Skin Type (30%)
    # -------------------------
    skin_type = (data.get("skin_type") or "").lower()

    if skin_type == "normal":
        score += 30
    elif skin_type == "combination":
        score += 25
    elif skin_type == "oily":
        score += 20
    elif skin_type == "dry":
        score += 15
    else:
        score += 20

    # -------------------------
    # 2. Concerns (30%)
    # -------------------------
    concerns = data.get("concerns") or []
    max_concern_score = 30

    penalty_per_concern = 8
    concern_penalty = len(concerns) * penalty_per_concern

    score += max(0, max_concern_score - concern_penalty)

    # -------------------------
    # 3. Sensitivity (15%)
    # -------------------------
    sensitivity = (data.get("sensitivity") or "").lower()

    if "not" in sensitivity:
        score += 15
    elif "slight" in sensitivity:
        score += 10
    elif "moderate" in sensitivity:
        score += 7
    elif "very" in sensitivity:
        score += 3
    else:
        score += 8

    # -------------------------
    # 4. Climate (10%)
    # -------------------------
    climate = (data.get("climate") or "").lower()

    if climate == "temperate":
        score += 10
    elif climate == "humid":
        score += 6
    elif climate == "cold":
        score += 5
    elif climate == "dry":
        score += 4
    else:
        score += 5

    # -------------------------
    # 5. Ingredients (10%)
    # -------------------------
    ingredients = data.get("ingredients") or []
    score += min(len(ingredients) * 3, 10)

    # -------------------------
    # 6. Allergies (5%)
    # -------------------------
    allergies = data.get("allergies") or []
    score += max(0, 5 - len(allergies) * 2)

    # -------------------------
    # FINAL SCORE (0–100)
    # -------------------------
    score = max(0, min(100, score))

    return int(score)


@app.route("/skin-score", methods=["POST"])
def skin_score():
    data = request.get_json(force=True)
    score = calculate_skin_score(data)
    return jsonify({"skin_score": score}), 200


# -----------------------------------
# DEBUG ROUTES
# -----------------------------------

@app.route('/debug/users')
def debug_users():
    """Returns all users from the database (for debugging purposes)"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        cursor.close()
        
        # Convert tuples to dict format
        results = []
        for row in data:
            results.append({
                "id": row[0],
                "email": row[1],
                "password": row[2],
                "full_name": row[3],
                "age": row[4],
                "gender": row[5]
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/debug/recommendations')
def debug_recommendations():
    """Returns all recommendations from the database (for debugging purposes)"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM recommendation")
        data = cursor.fetchall()
        cursor.close()
        
        # Convert tuples to dict format
        results = []
        for row in data:
            results.append({
                "id": row[0],
                "user_id": row[1],
                "product": row[2],
                "skin_score": row[3],
                "skin_type": row[4],
                "status": row[5],
                "created_at": str(row[6]) if row[6] else None
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/debug/surveys')
def debug_surveys():
    """Returns all surveys from the database (for debugging purposes)"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM skin_surveys")
        data = cursor.fetchall()
        cursor.close()
        
        # Convert tuples to dict format
        results = []
        for row in data:
            results.append({
                "id": row[0],
                "user_id": row[1],
                "skin_type": row[2],
                "concerns": row[3],
                "sensitivity": row[4],
                "climate": row[5],
                "ingredients": row[6],
                "allergies": row[7],
                "skin_score": row[8],
                "created_at": str(row[9]) if row[9] else None
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def handle_404(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found. Please check the URL and method.",
        "path": request.path
    }), 404


@app.errorhandler(405)
def handle_405(error):
    return jsonify({
        "status": "error",
        "message": "Method not allowed. Check HTTP method for this endpoint.",
        "path": request.path
    }), 405


# -----------------------------------
# RUN
# -----------------------------------

if __name__ == "__main__":
    # Disable the auto-reloader to avoid multiple model loads and repeated logs.
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
