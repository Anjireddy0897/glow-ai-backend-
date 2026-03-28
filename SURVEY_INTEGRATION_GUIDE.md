# Skin Survey Integration - Implementation Guide

## Overview
The skin survey has been properly integrated with the backend. Users can now:
1. Complete a skin survey
2. Receive an immediate score and rating
3. View their survey results on the home screen
4. Track their skin health progress

## Updated Endpoints

### 1. **POST /api/submit_survey/**
Submit a skin survey and get immediate results.

**Request:**
```json
{
  "user_id": 1,
  "skin_type": "oily",
  "concerns": ["Acne", "Excess Oil"],
  "sensitivity": "Normal",
  "climate": "Tropical",
  "ingredients": ["Salicylic Acid", "Niacinamide"],
  "allergies": []
}
```

**Response (with enhanced details):**
```json
{
  "status": "success",
  "message": "Survey saved successfully",
  "survey": {
    "skin_score": 85,
    "score_rating": "Excellent",
    "skin_type": "oily",
    "concerns": ["Acne", "Excess Oil"],
    "sensitivity": "Normal",
    "climate": "Tropical",
    "ingredients": ["Salicylic Acid", "Niacinamide"],
    "allergies": []
  }
}
```

**Frontend Usage:**
```javascript
// After user completes survey, submit it
const response = await fetch('/api/submit_survey/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(surveyData)
});

const result = await response.json();

// Display the score and rating immediately
if (result.status === 'success') {
  showScore(result.survey.skin_score);
  showRating(result.survey.score_rating);
  // You have all survey data ready for display
}
```

---

### 2. **GET /api/get_latest_survey/<user_id>** (NEW)
Retrieve the user's latest survey with full details.

**Request:**
```
GET /api/get_latest_survey/1
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "survey_id": 1,
    "skin_type": "oily",
    "concerns": ["Acne", "Excess Oil"],
    "sensitivity": "Normal",
    "climate": "Tropical",
    "ingredients": ["Salicylic Acid", "Niacinamide"],
    "allergies": [],
    "skin_score": 85,
    "score_rating": "Excellent",
    "created_at": "2026-03-25 14:30:45"
  }
}
```

**Frontend Usage:**
```javascript
// Load survey results to display on home screen
fetch(`/api/get_latest_survey/${userId}`)
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      displaySurveyScore(data.data.skin_score);
      displaySurveyRating(data.data.score_rating);
      displaySurveyDetails(data.data);
    }
  });
```

---

### 3. **GET /api/get_home_screen/<user_id>** (NEW)
Get combined home screen data including user info, survey data, and analytics.

**Request:**
```
GET /api/get_home_screen/1
```

**Response:**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  },
  "analytics": {
    "total_surveys": 5,
    "total_scans": 3,
    "total_analyses": 8
  },
  "latest_survey": {
    "score": 85,
    "score_rating": "Excellent",
    "skin_type": "oily",
    "date": "25/03/2026"
  }
}
```

**Frontend Usage:**
```javascript
// Load home screen with all necessary data in one call
fetch(`/api/get_home_screen/${userId}`)
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      // Display user greeting
      greetUser(data.user.name);
      
      // Display analytics
      showAnalytics(data.analytics.total_surveys);
      
      // Display latest score prominently
      if (data.latest_survey) {
        displayHomepageScore(data.latest_survey);
      }
    }
  });
```

---

## Score Rating System

The `score_rating` is automatically calculated based on the skin score (0-100):

| Score Range | Rating | Meaning |
|------------|--------|---------|
| 80-100 | Excellent | Skin health is good |
| 60-79 | Good | Skin is healthy with minor concerns |
| 40-59 | Fair | Skin needs attention |
| 0-39 | Needs Care | Significant skin concerns |

---

## Database Schema

The survey data is stored in the `skin_surveys` table:

```sql
CREATE TABLE skin_surveys (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  skin_type VARCHAR(50),
  concerns TEXT,
  sensitivity VARCHAR(50),
  climate VARCHAR(50),
  ingredients TEXT,
  allergies TEXT,
  skin_score INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Testing the Integration

Run the test script:
```bash
cd c:\facecream
python test_survey_integration.py
```

This will:
1. Submit a test survey
2. Retrieve the latest survey
3. Get home screen data
4. Display formatted results

---

## Frontend Implementation Example

### Home Screen Display

```html
<!-- Home Screen Component -->
<div class="home-screen">
  <div class="greeting">
    <h1>Welcome, <span id="userName">User</span>!</h1>
  </div>
  
  <div class="skin-score-card">
    <div class="score-display">
      <div class="score" id="skinScore">--</div>
      <div class="rating" id="scoreRating">No Data</div>
    </div>
    <div class="score-details">
      <p>Skin Type: <span id="skinType">--</span></p>
      <p>Last Updated: <span id="lastDate">--</span></p>
    </div>
  </div>
  
  <div class="analytics">
    <div class="stat">
      <p class="stat-label">Total Surveys</p>
      <p class="stat-value" id="totalSurveys">0</p>
    </div>
    <div class="stat">
      <p class="stat-label">Total Analyses</p>
      <p class="stat-value" id="totalAnalyses">0</p>
    </div>
  </div>
</div>

<script>
// Load home screen data
async function loadHomeScreen(userId) {
  try {
    const response = await fetch(`/api/get_home_screen/${userId}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      // Update user greeting
      document.getElementById('userName').textContent = data.user.name;
      
      // Update analytics
      document.getElementById('totalSurveys').textContent = 
        data.analytics.total_surveys;
      document.getElementById('totalAnalyses').textContent = 
        data.analytics.total_analyses;
      
      // Update score display
      if (data.latest_survey) {
        document.getElementById('skinScore').textContent = 
          data.latest_survey.score;
        document.getElementById('scoreRating').textContent = 
          data.latest_survey.score_rating;
        document.getElementById('skinType').textContent = 
          data.latest_survey.skin_type;
        document.getElementById('lastDate').textContent = 
          data.latest_survey.date;
      }
    }
  } catch (error) {
    console.error('Error loading home screen:', error);
  }
}

// Call on page load
loadHomeScreen(userId);
</script>
```

---

## What Changed

✅ **Enhanced `/api/submit_survey/` endpoint:**
- Now returns complete survey data with score rating
- Allows immediate display of results after submission

✅ **New `/api/get_latest_survey/<user_id>` endpoint:**
- Retrieves full survey details with formatted data
- Perfect for dedicated survey results page

✅ **New `/api/get_home_screen/<user_id>` endpoint:**
- Single call to get all home screen data
- Includes user info, analytics, and latest survey

✅ **New `get_score_rating()` helper function:**
- Converts numeric scores to readable ratings
- Used by all endpoints

---

## Next Steps (Optional)

1. **Survey History Page:** Use `/api/get_all_recommendations/<user_id>` to show survey history with trends
2. **Recommendations:** Generate skincare recommendations based on survey results
3. **Notifications:** Alert users when survey score improves/worsens
4. **Progress Tracking:** Show score progression over time with charts

---

## Database Connection Status

The backend is configured to connect to the `antireddy` database:
- Host: localhost
- Port: 3306
- Database: antireddy
- Tables: users, skin_surveys, recommendation

✓ Connection verified and working!
