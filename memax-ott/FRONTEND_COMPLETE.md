# 🎨 MEMAX OTT - Frontend Complete (Static Mode)

The frontend has been deployed as a **Integrated Static Application** served directly by your Python backend. This eliminates the need for Node.js/NPM installation while maintaining the full Cyberpunk experience.

## 🚀 Key Features Implemented

### 1. **Cyberpunk Aesthetic**
*   **Theme:** Violet/Black/Neon design system.
*   **Visuals:** Glassmorphism, glow effects, and responsive layouts.
*   **Tech Stack:** Vanilla HTML/CSS/JS (Lightweight & Fast).

### 2. **Authentication System**
*   **Login/Signup:** Fully functional forms connected to `/api/auth` endpoints.
*   **Security:** JWT token storage in `localStorage`.
*   **User Flow:** Signup -> Login -> Dashboard.

### 3. **Movie Dashboard**
*   **Trending:** Fetches data from `/api/movies/trending`.
*   **New Releases:** Fetches from `/api/movies/featured`.
*   **Fallback:** Automatic mock data if the API returns empty results.

---

## 🖥️ How to Run the Website

### Step 1: Ensure Backend is Running
Make sure the Python backend is running (it should be running now).
If not, run `START_BACKEND.bat`.

### Step 2: Open the Website
Double-click **`START_WEBSITE.bat`** on your desktop.

OR open this URL in your browser:
**<http://localhost:8000/static/index.html>**

---

## 📂 Project Structure (`/backend/app/static`)

```text
backend/app/static/
├── index.html        # Main Dashboard
├── login.html        # Authentication
├── signup.html       # Registration
├── css/
│   └── style.css     # Cyberpunk Styles
└── js/
    └── app.js        # Logic & API Integration
```

---

## ✅ Verified Status
*   **Backend:** Running on Port 8000.
*   **Database:** Dataset import started (check backend logs for progress).
*   **Frontend:** Accessible via `/static` endpoint.
*   **Auth:** Connected to PostgreSQL database.

Enjoy your streaming platform! 🍿🎥
