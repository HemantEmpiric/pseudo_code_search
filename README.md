# Restaurant Finder

A Django-based restaurant search application that integrates directly with Google Places APIs to find and display restaurant information.

## Features

- **Search Interface**: Clean, modern search interface for finding restaurants
- **Google Places APIs**: Direct integration with:
  - Places Text Search API for finding restaurants
  - Places Details API for comprehensive restaurant information
  - Places Photos API for restaurant images
- **Mock Data Support**: Works without API key using sample data for testing
- **Restaurant Profiles**: Detailed restaurant information including:
  - Basic info (name, address, contact, website)
  - Operating hours
  - Amenities and features
  - Vibe classification
  - Photos and images
  - Reservation information
- **Smart Caching**: In-memory caching for improved performance
- **Responsive Design**: Mobile-friendly Bootstrap-based UI

## Project Structure

```
restaurant_finder/
├── restaurant_finder/          # Main Django project
│   ├── settings.py            # Django settings
│   └── urls.py               # Main URL configuration
├── restaurants/               # Main app
│   ├── models.py             # Data structures and cache logic
│   ├── services.py           # Google Places API integration
│   ├── views.py              # Django views
│   └── urls.py               # App URL configuration
├── templates/                 # HTML templates
│   └── restaurants/
│       └── main.html         # Main search interface
├── static/                    # Static files (CSS, JS)
├── manage.py                  # Django management script
└── README.md                  # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Google Maps API key with Places API enabled

### 2. Installation

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd /path/to/restaurant_finder
   ```

3. Create and activate a virtual environment:
   ```bash
   python3.10 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root:
   ```bash
   # Google Maps API Configuration
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   
   # Django Configuration
   DEBUG=True
   SECRET_KEY=your_django_secret_key_here
   ```

6. Run the development server:
   ```bash
   python3 manage.py runserver
   ```

7. Open your browser and navigate to `http://127.0.0.1:8000/`

## API Endpoints

- `GET /` - Main search page
- `POST /search/` - Search for restaurants
- `GET /details/?place_id={id}` - Get restaurant details
- `GET /clear-cache/` - Clear the in-memory cache

## Usage

1. **Search**: Enter a restaurant name, cuisine type, or location in the search box
2. **Browse Results**: View search results with basic restaurant information
3. **View Details**: Click on any restaurant card to see detailed information
4. **Navigate**: Use the back button to return to search results

## Configuration

### Google Places APIs

To use this application, you need a Google Maps API key with the following APIs enabled:
- **Places API** - for restaurant search and details
- **Places Photos API** - for restaurant images
- **Geocoding API** (optional, for enhanced location search)

Get your API key from the [Google Cloud Console](https://console.cloud.google.com/).

### Environment Variables

Create a `.env` file with the following variables:
- `GOOGLE_MAPS_API_KEY`: Your Google Places API key
- `DEBUG`: Django debug mode (True/False)
- `SECRET_KEY`: Django secret key

## Features Implementation

### Search Functionality
- Implements the `search_view` function from your pseudo code
- Calls Google Places Text Search API
- Caches results for improved performance

### Restaurant Details
- Implements the `details_view` function from your pseudo code
- Retrieves comprehensive restaurant information
- Includes amenities, vibes, and operating hours

### Caching
- Simple in-memory cache with TTL (Time To Live)
- Caches both search results and restaurant details
- Cache can be cleared via `/clear-cache/` endpoint

### Vibe Classification
- Basic vibe classification based on amenities and restaurant types
- Extensible system for adding more sophisticated classification logic

## Future Enhancements

- Database integration for persistent storage
- User accounts and favorites
- Advanced filtering and sorting
- Reservation booking integration
- Review and rating system
- Social media integration
- AI-powered recommendations

## Troubleshooting

### Common Issues

1. **Google Places API Error**: Ensure your API key is valid and has the Places API and Places Photos API enabled
2. **No Results**: Check if your search query is specific enough
3. **Cache Issues**: Use the `/clear-cache/` endpoint to reset the cache

### Debug Mode

When `DEBUG=True` in your `.env` file, Django will show detailed error messages for development purposes.

## License

This project is private and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.
