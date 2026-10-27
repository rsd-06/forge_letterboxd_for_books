import os
import logging
from datetime import datetime, timezone
from django.conf import settings

logger = logging.getLogger(__name__)

_mongo_client = None
_mongo_db = None


def get_mongo_db():
    """
    Connect to MongoDB database using MONGODB_URI environment variable.
    Returns (db, status_string).
    """
    global _mongo_client, _mongo_db
    if _mongo_db is not None:
        return _mongo_db, "Connected"

    mongo_uri = getattr(settings, 'MONGODB_URI', '') or os.getenv('MONGODB_URI', '')
    if not mongo_uri or not mongo_uri.strip():
        return None, "Not configured (Set MONGODB_URI in .env)"

    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Test connection
        _mongo_client.admin.command('ping')
        db_name = getattr(settings, 'MONGODB_NAME', 'bookboxd')
        _mongo_db = _mongo_client[db_name]
        return _mongo_db, "Connected"
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}")
        return None, f"Connection Failed: {str(e)[:60]}"


def log_chat_to_mongo(session_id, user_id, username, message, response, is_live_ai=False):
    """
    Save user chat interactions to MongoDB 'chat_logs' collection.
    """
    db, status = get_mongo_db()
    record = {
        'session_id': session_id,
        'user_id': user_id,
        'username': username or 'anonymous',
        'message': message,
        'response': response,
        'is_live_ai': is_live_ai,
        'timestamp': datetime.now(timezone.utc),
    }
    if db is not None:
        try:
            db.chat_logs.insert_one(record)
            return True
        except Exception as e:
            logger.error(f"Error logging chat to Mongo: {e}")
    # Local fallback log if mongo not configured
    logger.info(f"[Chat Log Fallback] {username}: {message[:40]} -> {response[:40]}")
    return False


def log_chat_feedback_to_mongo(chat_id, user_id, rating, feedback_text):
    """
    Save chat feedback to MongoDB 'chat_feedback' collection.
    """
    db, status = get_mongo_db()
    record = {
        'chat_id': chat_id,
        'user_id': user_id,
        'rating': rating,
        'feedback_text': feedback_text,
        'timestamp': datetime.now(timezone.utc),
    }
    if db is not None:
        try:
            db.chat_feedback.insert_one(record)
            return True
        except Exception as e:
            logger.error(f"Error logging feedback to Mongo: {e}")
    return False


def log_user_crud_to_mongo(action, user_data):
    """
    Audit log of User CRUD operations (create, update, friend toggle).
    """
    db, status = get_mongo_db()
    record = {
        'action': action,  # 'CREATE_USER', 'UPDATE_PROFILE', 'FRIEND_TOGGLE'
        'data': user_data,
        'timestamp': datetime.now(timezone.utc),
    }
    if db is not None:
        try:
            db.user_crud_logs.insert_one(record)
            return True
        except Exception as e:
            logger.error(f"Error logging user CRUD to Mongo: {e}")
    return False


def log_book_crud_to_mongo(action, book_data):
    """
    Audit log of Book & Review CRUD operations (rate, review, shelf add/remove, comment).
    """
    db, status = get_mongo_db()
    record = {
        'action': action,  # 'CREATE_BOOK', 'RATE_REVIEW', 'ADD_TO_SHELF', 'ADD_COMMENT'
        'data': book_data,
        'timestamp': datetime.now(timezone.utc),
    }
    if db is not None:
        try:
            db.book_crud_logs.insert_one(record)
            return True
        except Exception as e:
            logger.error(f"Error logging book CRUD to Mongo: {e}")
    return False


def log_request_to_mongo(method, path, status_code, ip_address, duration_ms):
    """
    Save HTTP request logs to MongoDB 'request_logs' collection.
    """
    db, status = get_mongo_db()
    if db is not None:
        try:
            db.request_logs.insert_one({
                'method': method,
                'path': path,
                'status_code': status_code,
                'ip_address': ip_address,
                'duration_ms': round(duration_ms, 2),
                'timestamp': datetime.now(timezone.utc),
            })
            return True
        except Exception as e:
            logger.debug(f"Error writing request log to Mongo: {e}")
    return False


def get_mongo_stats():
    """
    Return statistics and counts from MongoDB for the health check.
    """
    db, status = get_mongo_db()
    if db is None:
        return {'status': status, 'is_connected': False}
    try:
        return {
            'status': 'Connected',
            'is_connected': True,
            'chat_logs_count': db.chat_logs.count_documents({}),
            'user_crud_count': db.user_crud_logs.count_documents({}),
            'book_crud_count': db.book_crud_logs.count_documents({}),
            'request_logs_count': db.request_logs.count_documents({}),
        }
    except Exception as e:
        return {'status': f"Error: {e}", 'is_connected': False}
