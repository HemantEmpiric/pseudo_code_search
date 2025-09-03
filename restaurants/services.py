from django.conf import settings
from typing import List, Dict, Optional, Tuple
import requests
import json
from .models import Restaurant, SearchResult, restaurant_cache


class GooglePlacesService:
    """Service for interacting with Google Places API directly"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        if not self.api_key or self.api_key == 'your_google_maps_api_key_here':
            self.api_key = None
            print("Warning: Google Places API key not configured. Please set GOOGLE_MAPS_API_KEY in your .env file")
        
        # Google Places API endpoints
        self.text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        self.photo_url = "https://maps.googleapis.com/maps/api/place/photo"
    
    def text_search(self, query: str) -> List[SearchResult]:
        """Perform text search using Google Places Text Search API"""
        try:
            # Check cache first
            cached_results = restaurant_cache.get_search_results(query)
            if cached_results:
                return cached_results
            
            # Check if API key is available
            if not self.api_key:
                return self._get_mock_search_results(query)
            
            # Prepare parameters for Google Places Text Search API
            params = {
                'query': query,
                'type': 'restaurant',
                'key': self.api_key,
                'language': 'en'
            }
            
            # Make request to Google Places Text Search API
            response = requests.get(self.text_search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                print(f"Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return self._get_mock_search_results(query)
            
            results = []
            for place in data.get('results', []):
                result = SearchResult(
                    place_id=place.get('place_id'),
                    name=place.get('name', ''),
                    address=place.get('formatted_address', ''),
                    rating=place.get('rating')
                )
                results.append(result)
            
            # Cache the results
            restaurant_cache.set_search_results(query, results)
            return results
            
        except Exception as e:
            print(f"Error in text search: {e}")
            return self._get_mock_search_results(query)
    
    def get_place_details(self, place_id: str) -> Optional[Restaurant]:
        """Get detailed information using Google Places Details API"""
        try:
            # Check cache first
            cached_restaurant = restaurant_cache.get_restaurant(place_id)
            if cached_restaurant:
                return cached_restaurant
            
            # Check if API key is available
            if not self.api_key:
                return self._get_mock_restaurant_details(place_id)
            
            # Prepare parameters for Google Places Details API
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,photos,rating,price_level,types,url',
                'key': self.api_key,
                'language': 'en'
            }
            
            # Make request to Google Places Details API
            response = requests.get(self.details_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                print(f"Google Places Details API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return self._get_mock_restaurant_details(place_id)
            
            place = data.get('result', {})
            if not place:
                return None
            
            # Create restaurant object
            restaurant = Restaurant(
                place_id=place_id,
                name=place.get('name', ''),
                address=place.get('formatted_address', ''),
                rating=place.get('rating'),
                contact=place.get('formatted_phone_number'),
                website=place.get('website'),
                operating_hours=self._format_hours(place.get('opening_hours')),
                images=self._extract_photos(place.get('photos', [])),
                amenities=self._extract_amenities(place),
                summaries=self._extract_summaries(place),
                vibes=self._classify_vibes(place),
                how_found={'reservation_url': 'google direct', 'images': 'google direct'}
            )
            
            # Get additional data
            restaurant.reservation_url, restaurant.reservation_partner, _ = self._get_reservation_url(
                restaurant.website, restaurant
            )
            restaurant.socials = self._get_social_links(restaurant.website)
            restaurant.menu_url = self._get_menu_url(restaurant.website)
            
            # Cache the restaurant
            restaurant_cache.set_restaurant(place_id, restaurant)
            return restaurant
            
        except Exception as e:
            print(f"Error getting place details: {e}")
            return self._get_mock_restaurant_details(place_id)
    
    def _format_hours(self, opening_hours: Optional[Dict]) -> Optional[Dict]:
        """Format opening hours with today highlighted and current day info"""
        if not opening_hours:
            return None
        
        from datetime import datetime
        today = datetime.now().weekday()  # Monday=0, Tuesday=1, ..., Sunday=6
        current_time = datetime.now().time()
        
        # Get today's hours
        today_hours = None
        if opening_hours.get('weekday_text') and len(opening_hours['weekday_text']) > today:
            today_hours = opening_hours['weekday_text'][today]
        
        # Check if currently open based on periods
        is_currently_open = False
        current_period = None
        if opening_hours.get('periods') and len(opening_hours['periods']) > today:
            today_periods = opening_hours['periods'][today]
            if today_periods.get('open') and today_periods.get('close'):
                # Parse opening and closing times
                open_time_str = today_periods['open']['time']
                close_time_str = today_periods['close']['time']
                
                # Convert to time objects for comparison
                open_time = datetime.strptime(open_time_str, '%H%M').time()
                close_time = datetime.strptime(close_time_str, '%H%M').time()
                
                # Handle cases where restaurant is open past midnight
                if close_time < open_time:  # Crosses midnight
                    is_currently_open = current_time >= open_time or current_time <= close_time
                else:
                    is_currently_open = open_time <= current_time <= close_time
                
                current_period = {
                    'open': open_time.strftime('%I:%M %p'),
                    'close': close_time.strftime('%I:%M %p'),
                    'is_open': is_currently_open
                }
        
        formatted_hours = {
            'periods': opening_hours.get('periods', []),
            'weekday_text': opening_hours.get('weekday_text', []),
            'today': today,
            'today_hours': today_hours,
            'current_period': current_period,
            'open_now': opening_hours.get('open_now', False) or is_currently_open,
            'day_names': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        }
        
        return formatted_hours
    
    def _extract_photos(self, photos: List[Dict]) -> List[str]:
        """Extract photo URLs using Google Places Photos API"""
        photo_urls = []
        for photo in photos[:10]:  # Limit to 10 photos
            if photo.get('photo_reference'):
                # Use Google Places Photos API to get actual photo URLs
                photo_url = f"{self.photo_url}?maxwidth=400&photoreference={photo['photo_reference']}&key={self.api_key}"
                photo_urls.append(photo_url)
        
        return photo_urls
    
    def _extract_amenities(self, place: Dict) -> Dict:
        """Extract amenities from place data"""
        types = place.get('types', [])
        
        amenities = {
            "dineIn": True,  # Default for restaurants
            "delivery": "delivery" in types or "takeout" in types,
            "takeout": "takeout" in types,
            "outdoorSeating": "outdoor_seating" in types,
            "liveMusic": False,  # Would need additional data
            "goodForGroups": "meal_takeaway" in types,
            "goodForChildren": "family_restaurant" in types,
            "servesDinner": True,  # Default for restaurants
            "servesLunch": True,  # Default for restaurants
            "servesWine": "bar" in types or "wine_bar" in types
        }
        
        return amenities
    
    def _extract_summaries(self, place: Dict) -> Dict:
        """Extract review and editorial summaries"""
        # In a real implementation, you'd get these from Google Places API
        # For now, return placeholder data
        return {
            "reviewSummary": f"Rated {place.get('rating', 'N/A')} by customers",
            "generativeSummary": "A popular dining destination",
            "editorialSummary": "Well-reviewed restaurant in the area"
        }
    
    def _classify_vibes(self, place: Dict) -> List[str]:
        """Classify restaurant vibes based on amenities and data"""
        vibes = []
        amenities = self._extract_amenities(place)
        
        if amenities.get("liveMusic"):
            vibes.append("Lively")
        if amenities.get("goodForChildren"):
            vibes.append("Family-friendly")
        if amenities.get("servesWine") and amenities.get("outdoorSeating"):
            vibes.append("Chill / Lounge")
        if place.get('price_level', 0) >= 4:
            vibes.append("Luxury dining")
        
        # Add more vibe classifications based on types
        types = place.get('types', [])
        if "romantic_restaurant" in types:
            vibes.append("Romantic")
        if "casual_restaurant" in types:
            vibes.append("Casual")
        if "fine_dining" in types:
            vibes.append("Fine Dining")
        
        # Limit to top 8 vibes
        return vibes[:8]
    
    def _get_reservation_url(self, website: Optional[str], restaurant: Restaurant) -> Tuple[Optional[str], str, str]:
        """Get reservation URL and partner information"""
        if not website:
            return None, "None", "no website"
        
        # In a real implementation, you'd scrape the website for reservation links
        # For now, return placeholder data
        return None, "None", "website analysis needed"
    
    def _get_social_links(self, website: Optional[str]) -> Dict:
        """Extract social media links from website"""
        if not website:
            return {}
        
        # In a real implementation, you'd scrape the website for social links
        # For now, return placeholder data
        return {
            "instagram": None,
            "facebook": None,
            "twitter": None
        }
    
    def _get_menu_url(self, website: Optional[str]) -> Optional[str]:
        """Extract menu URL from website"""
        if not website:
            return None
        
        # In a real implementation, you'd scrape the website for menu links
        # For now, return placeholder data
        return None
    
    def _get_mock_search_results(self, query: str) -> List[SearchResult]:
        """Return mock search results when API key is not configured"""
        mock_results = [
            SearchResult(
                place_id="mock_place_1",
                name=f"Sample Restaurant for '{query}'",
                address="123 Main Street, Sample City, SC 12345",
                rating=4.5
            ),
            SearchResult(
                place_id="mock_place_2", 
                name=f"Another Restaurant for '{query}'",
                address="456 Oak Avenue, Sample City, SC 12345",
                rating=4.2
            ),
            SearchResult(
                place_id="mock_place_3",
                name=f"Third Restaurant for '{query}'",
                address="789 Pine Road, Sample City, SC 12345",
                rating=3.8
            )
        ]
        
        # Cache the mock results
        restaurant_cache.set_search_results(query, mock_results)
        return mock_results
    
    def _get_mock_restaurant_details(self, place_id: str) -> Optional[Restaurant]:
        """Return mock restaurant details when API key is not configured"""
        mock_restaurant = Restaurant(
            place_id=place_id,
            name="Sample Restaurant",
            address="123 Main Street, Sample City, SC 12345",
            rating=4.5,
            contact="(555) 123-4567",
            website="https://example-restaurant.com",
            reservation_url=None,
            reservation_partner="None",
            operating_hours={
                'weekday_text': [
                    'Monday: 11:00 AM – 10:00 PM',
                    'Tuesday: 11:00 AM – 10:00 PM', 
                    'Wednesday: 11:00 AM – 10:00 PM',
                    'Thursday: 11:00 AM – 10:00 PM',
                    'Friday: 11:00 AM – 11:00 PM',
                    'Saturday: 10:00 AM – 11:00 PM',
                    'Sunday: 10:00 AM – 9:00 PM'
                ],
                'periods': [
                    {'open': {'day': 0, 'time': '1100'}, 'close': {'day': 0, 'time': '2200'}},
                    {'open': {'day': 1, 'time': '1100'}, 'close': {'day': 1, 'time': '2200'}},
                    {'open': {'day': 2, 'time': '1100'}, 'close': {'day': 2, 'time': '2200'}},
                    {'open': {'day': 3, 'time': '1100'}, 'close': {'day': 3, 'time': '2200'}},
                    {'open': {'day': 4, 'time': '1100'}, 'close': {'day': 4, 'time': '2300'}},
                    {'open': {'day': 5, 'time': '1000'}, 'close': {'day': 5, 'time': '2300'}},
                    {'open': {'day': 6, 'time': '1000'}, 'close': {'day': 6, 'time': '2100'}}
                ],
                'open_now': True
            },
            socials={
                "instagram": "https://instagram.com/sample_restaurant",
                "facebook": "https://facebook.com/sample_restaurant",
                "twitter": None
            },
            menu_url="https://example-restaurant.com/menu",
            amenities={
                "dineIn": True,
                "delivery": True,
                "takeout": True,
                "outdoorSeating": True,
                "liveMusic": False,
                "goodForGroups": True,
                "goodForChildren": True,
                "servesDinner": True,
                "servesLunch": True,
                "servesWine": True
            },
            summaries={
                "reviewSummary": "Highly rated restaurant with excellent food and service",
                "generativeSummary": "A popular dining destination known for its quality cuisine",
                "editorialSummary": "Well-reviewed restaurant in the heart of the city"
            },
            vibes=["Family-friendly", "Casual", "Good for Groups"],
            images=[
                "https://via.placeholder.com/400x300/667eea/ffffff?text=Restaurant+Image+1",
                "https://via.placeholder.com/400x300/764ba2/ffffff?text=Restaurant+Image+2"
            ],
            how_found={
                "reservation_url": "mock data",
                "images": "mock data"
            }
        )
        
        # Cache the mock restaurant
        restaurant_cache.set_restaurant(place_id, mock_restaurant)
        return mock_restaurant


# Global service instance
places_service = GooglePlacesService()
