from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


@dataclass
class Restaurant:
    """Simple data structure for restaurant information"""
    place_id: str
    name: str
    address: str
    rating: Optional[float] = None
    contact: Optional[str] = None
    website: Optional[str] = None
    reservation_url: Optional[str] = None
    reservation_partner: Optional[str] = None
    operating_hours: Optional[Dict] = None
    socials: Optional[Dict] = None
    menu_url: Optional[str] = None
    amenities: Optional[Dict] = None
    summaries: Optional[Dict] = None
    vibes: Optional[List[str]] = None
    images: Optional[List[str]] = None
    how_found: Optional[Dict] = None


@dataclass
class SearchResult:
    """Simple data structure for search results"""
    place_id: str
    name: str
    address: str
    rating: Optional[float] = None


# Simple in-memory cache
class RestaurantCache:
    """Simple in-memory cache for restaurant data"""
    
    def __init__(self):
        self.restaurants = {}
        self.search_cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    def get_restaurant(self, place_id: str) -> Optional[Restaurant]:
        """Get restaurant from cache"""
        if place_id in self.restaurants:
            restaurant, timestamp = self.restaurants[place_id]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return restaurant
            else:
                del self.restaurants[place_id]
        return None
    
    def set_restaurant(self, place_id: str, restaurant: Restaurant):
        """Cache restaurant data"""
        self.restaurants[place_id] = (restaurant, datetime.now())
    
    def get_search_results(self, query: str) -> Optional[List[SearchResult]]:
        """Get search results from cache"""
        if query in self.search_cache:
            results, timestamp = self.search_cache[query]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return results
            else:
                del self.search_cache[query]
        return None
    
    def set_search_results(self, query: str, results: List[SearchResult]):
        """Cache search results"""
        self.search_cache[query] = (results, datetime.now())
    
    def clear_cache(self):
        """Clear all cached data"""
        self.restaurants.clear()
        self.search_cache.clear()


# Global cache instance
restaurant_cache = RestaurantCache()
