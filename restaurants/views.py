from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .services import places_service
from .models import restaurant_cache


def main_page(request):
    """Main page view - renders search textbox"""
    return render(request, 'restaurants/main.html')


@csrf_exempt
@require_http_methods(["POST"])
def search_view(request):
    """Search view - handles restaurant search"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        
        if not query:
            return JsonResponse({
                'error': 'Query cannot be empty'
            }, status=400)
        
        # Call Google Places API for search
        results = places_service.text_search(query)
        
        # Convert to serializable format
        serialized_results = []
        for result in results:
            serialized_results.append({
                'place_id': result.place_id,
                'name': result.name,
                'address': result.address,
                'rating': result.rating
            })
        
        return JsonResponse({
            'results': serialized_results
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Search failed: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def details_view(request):
    """Details view - gets restaurant details by place_id"""
    place_id = request.GET.get('place_id')
    
    if not place_id:
        return JsonResponse({
            'error': 'place_id is required'
        }, status=400)
    
    # Get restaurant details from Google Places API
    restaurant = places_service.get_place_details(place_id)
    
    if not restaurant:
        return JsonResponse({
            'error': 'Restaurant not found'
        }, status=404)
    
    # Convert to serializable format
    serialized_restaurant = {
        'id': str(hash(restaurant.place_id)),  # Simple ID generation
        'place_id': restaurant.place_id,
        'name': restaurant.name,
        'address': restaurant.address,
        'contact': restaurant.contact,
        'website': restaurant.website,
        'reservation_url': restaurant.reservation_url,
        'reservation_partner': restaurant.reservation_partner,
        'operating_hours': restaurant.operating_hours,
        'socials': restaurant.socials,
        'menu_url': restaurant.menu_url,
        'amenities': restaurant.amenities,
        'summaries': restaurant.summaries,
        'vibes': restaurant.vibes,
        'images': restaurant.images,
        'how_found': restaurant.how_found
    }
    
    return JsonResponse(serialized_restaurant)


@require_http_methods(["GET"])
def clear_cache(request):
    """Clear the in-memory cache"""
    restaurant_cache.clear_cache()
    return JsonResponse({
        'message': 'Cache cleared successfully'
    })
