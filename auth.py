"""
Authentication and User Database Module
Provides secure user registration, bcrypt password hashing, and user trip persistence in PostgreSQL.
"""

import os
import re
import bcrypt
import psycopg
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Establish and return an autocommit connection to PostgreSQL, or None if unavailable."""
    if not DATABASE_URL or DATABASE_URL.startswith("your_") or "postgres:postgres@" in DATABASE_URL:
        return None
    try:
        conn = psycopg.connect(DATABASE_URL, autocommit=True)
        return conn
    except Exception as e:
        print(f"⚠️ [Auth DB] Database connection error: {e}")
        return None


def init_db():
    """Initialize user and trip history tables if they do not exist."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS app_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_trips (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES app_users(id) ON DELETE CASCADE,
                    destination VARCHAR(100),
                    query TEXT NOT NULL,
                    plan_title VARCHAR(255),
                    flight_results TEXT,
                    hotel_results TEXT,
                    weather_results TEXT,
                    itinerary TEXT,
                    final_response TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ [Auth DB] Schema initialization error: {e}")
        if conn:
            conn.close()
        return False


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with a cryptographically secure salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def validate_registration_input(username: str, email: str, password: str) -> tuple[bool, str]:
    """Validate username, email, and password format."""
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters long."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username.strip()):
        return False, "Username may only contain letters, numbers, hyphens, and underscores."
    
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not email or not re.match(email_regex, email.strip()):
        return False, "Please enter a valid email address."

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."

    return True, ""


def register_user(username: str, email: str, password: str, full_name: str = "") -> tuple[bool, str]:
    """Register a new user with hashed password in PostgreSQL."""
    valid, msg = validate_registration_input(username, email, password)
    if not valid:
        return False, msg

    conn = get_db_connection()
    if not conn:
        return False, "Database is currently offline. Please check your PostgreSQL connection."

    username_clean = username.strip().lower()
    email_clean = email.strip().lower()
    pwd_hash = hash_password(password)

    try:
        with conn.cursor() as cur:
            # Check for existing username or email
            cur.execute("SELECT id FROM app_users WHERE username = %s OR email = %s;", [username_clean, email_clean])
            if cur.fetchone():
                conn.close()
                return False, "A user with that username or email already exists."

            cur.execute("""
                INSERT INTO app_users (username, email, password_hash, full_name)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, [username_clean, email_clean, pwd_hash, full_name.strip() or username_clean])
            new_id = cur.fetchone()[0]

        conn.close()
        return True, "Registration successful! You can now log in."
    except Exception as e:
        if conn:
            conn.close()
        return False, f"Registration failed: {str(e)}"


def authenticate_user(identifier: str, password: str) -> tuple[dict | None, str]:
    """Authenticate user by username or email and return user dictionary."""
    if not identifier or not password:
        return None, "Please provide both username/email and password."

    conn = get_db_connection()
    if not conn:
        return None, "Database is currently offline."

    clean_id = identifier.strip().lower()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, username, email, password_hash, full_name, created_at
                FROM app_users
                WHERE username = %s OR email = %s;
            """, [clean_id, clean_id])
            row = cur.fetchone()

        conn.close()

        if not row:
            return None, "Invalid username or password."

        user_id, username, email, pwd_hash, full_name, created_at = row

        if not verify_password(password, pwd_hash):
            return None, "Invalid username or password."

        return {
            "id": user_id,
            "username": username,
            "email": email,
            "full_name": full_name or username,
            "created_at": created_at,
        }, "Login successful."
    except Exception as e:
        if conn:
            conn.close()
        return None, f"Authentication error: {str(e)}"


def save_user_trip(user_id: int, query: str, destination: str, plan_title: str,
                   flight_results: str, hotel_results: str, weather_results: str,
                   itinerary: str, final_response: str) -> bool:
    """Save a generated trip package for the authenticated user."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_trips (
                    user_id, destination, query, plan_title,
                    flight_results, hotel_results, weather_results,
                    itinerary, final_response
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, [
                user_id, destination, query, plan_title,
                flight_results, hotel_results, weather_results,
                itinerary, final_response
            ])
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error saving user trip: {e}")
        if conn:
            conn.close()
        return False


def get_user_trips(user_id: int) -> list[dict]:
    """Retrieve all saved travel packages for a specific user, newest first."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, destination, query, plan_title,
                       flight_results, hotel_results, weather_results,
                       itinerary, final_response, created_at
                FROM user_trips
                WHERE user_id = %s
                ORDER BY created_at DESC;
            """, [user_id])
            rows = cur.fetchall()
        conn.close()

        trips = []
        for r in rows:
            trips.append({
                "id": r[0],
                "destination": r[1],
                "query": r[2],
                "plan_title": r[3],
                "flight_results": r[4],
                "hotel_results": r[5],
                "weather_results": r[6],
                "itinerary": r[7],
                "final_response": r[8],
                "created_at": r[9],
            })
        return trips
    except Exception as e:
        print(f"⚠️ Error fetching user trips: {e}")
        if conn:
            conn.close()
        return []


def delete_user_trip(trip_id: int, user_id: int) -> bool:
    """Delete a specific trip belonging to the authenticated user."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM user_trips WHERE id = %s AND user_id = %s;", [trip_id, user_id])
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Error deleting trip: {e}")
        if conn:
            conn.close()
        return False


# Auto-initialize tables on module import
init_db()
