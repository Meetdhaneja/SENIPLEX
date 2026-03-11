# MEMAX OTT Platform - Testing Guide

## 1. Using Postman

We have created a Postman collection to simplify API testing.

1.  **Import Collection**:
    *   Open Postman.
    *   Click "Import" -> "File" -> "Upload Files".
    *   Select `memax_postman_collection.json` from the project root.

2.  **Environment Setup**:
    *   The collection includes a `base_url` variable set to `http://localhost:8000`.
    *   It also has `access_token` and `refresh_token` variables which are automatically updated after a successful login.

3.  **Run Tests**:
    *   **Login**: Open the "Auth" -> "Login" request. Click "Send". Verify you get a 200 OK and tokens.
    *   **Get User**: Open "Auth" -> "Get Current User". Click "Send". Verify you see the admin user details.
    *   **Get Likes**: Open "Movies" -> "Get Likes". Click "Send". Verify you get an empty list (or list of likes).
    *   **Recommendations**: Open "Movies" -> "Get Personalized Recommendations". Click "Send". Verify you get movie recommendations.

## 2. Manual Frontend Testing

Since automated browser testing is currently unavailable, please verify the frontend manually:

1.  **Start Servers**:
    *   Ensure backend is running: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` (Backend directory)
    *   Ensure frontend is running: `npm run dev` (Frontend directory)

2.  **Login Flow**:
    *   Open your browser and navigate to `http://localhost:3000/login`.
    *   Enter credentials:
        *   **Email**: `admin@memax.com`
        *   **Password**: `admin123`
    *   Click "Sign In".
    *   Verify you are redirected to the home page (`http://localhost:3000`).
    *   Verify you see user-specific content (e.g., "My List", "Account").

3.  **Recommendations**:
    *   On the home page, scroll down to see "Recommended for You".
    *   Verify movies are displayed.
