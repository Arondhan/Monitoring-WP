"""
Services package
"""
from app.services.wordpress import WordPressService, get_wordpress_service

__all__ = ["WordPressService", "get_wordpress_service"]
