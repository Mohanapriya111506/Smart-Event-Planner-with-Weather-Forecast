from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# In-memory data storage
events = {}
weather_cache = {}
event_counter = 1

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '1a6b02cacdb153159a4e82b8e8f8a3c7')
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

# Event type weather preferences with new scoring system
EVENT_WEATHER_PREFERENCES = {
    'sports': {
        'name': 'Sports Event',
        'scoring': {
            'temperature': {
                'ideal_range': (18, 28),
                'acceptable_range': (15, 32),
                'max_points': 30,
                'acceptable_points': 15
            },
            'precipitation': {
                'ideal_max': 10,
                'acceptable_max': 30,
                'max_points': 30,
                'acceptable_points': 15
            },
            'wind': {
                'ideal_max': 15,
                'acceptable_max': 25,
                'max_points': 25,
                'acceptable_points': 12
            },
            'conditions': {
                'max_points': 15,
                'scores': {
                    'clear': 15,
                    'partly cloudy': 15,
                    'overcast': 10,
                    'light rain': 5,
                    'heavy rain': 0,
                    'thunderstorm': 0
                }
            }
        },
        'total_max_score': 100
    },
    'formal': {
        'name': 'Formal Event',
        'scoring': {
            'precipitation': {
                'ideal_max': 0,
                'acceptable_max': 10,
                'max_points': 40,
                'acceptable_points': 20
            },
            'temperature': {
                'ideal_range': (20, 26),
                'acceptable_range': (18, 29),
                'max_points': 30,
                'acceptable_points': 15
            },
            'humidity': {
                'ideal_range': (40, 60),
                'acceptable_range': (30, 70),
                'max_points': 20,
                'acceptable_points': 10
            },
            'wind': {
                'ideal_max': 10,
                'acceptable_max': 15,
                'max_points': 10,
                'acceptable_points': 5
            }
        },
        'total_max_score': 100
    },
    'adventure': {
        'name': 'Outdoor Adventure',
        'scoring': {
            'temperature': {
                'ideal_range': (10, 25),
                'acceptable_range': (5, 30),
                'max_points': 30,
                'acceptable_points': 15
            },
            'precipitation': {
                'ideal_max': 15,
                'acceptable_max': 30,
                'max_points': 25,
                'acceptable_points': 12
            },
            'visibility': {
                'ideal_min': 10,
                'acceptable_min': 5,
                'max_points': 25,
                'acceptable_points': 15
            },
            'wind': {
                'ideal_range': (5, 20),
                'acceptable_range': (0, 30),
                'max_points': 20,
                'acceptable_points': 10
            }
        },
        'total_max_score': 100
    },
    'picnic': {
        'name': 'Family/Friends Picnic',
        'scoring': {
            'comfort': {
                'ideal_range': (18, 27),
                'acceptable_range': (15, 30),
                'max_points': 40,
                'acceptable_points': 25
            },
            'precipitation': {
                'ideal_max': 0,
                'acceptable_max': 15,
                'max_points': 30,
                'acceptable_points': 15
            },
            'uv_index': {
                'ideal_max': 3,
                'acceptable_max': 6,
                'max_points': 20,
                'acceptable_points': 15,
                'high_points': 5
            },
            'wind': {
                'ideal_range': (5, 15),
                'acceptable_range': (0, 20),
                'max_points': 10,
                'acceptable_points': 5
            }
        },
        'total_max_score': 100
    }
}

def get_weather_data(location, date=None):
    """Fetch weather data from OpenWeatherMap API"""
    cache_key = f"{location}_{date}" if date else location
    
    # Check cache first
    if cache_key in weather_cache:
        cached_data = weather_cache[cache_key]
        if time.time() - cached_data['timestamp'] < 21600:  # 6 hours cache
            return cached_data['data']
    
    try:
        if date:
            # Get 5-day forecast
            url = f"{OPENWEATHER_BASE_URL}/forecast"
            params = {
                'q': location,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
        else:
            # Get current weather
            url = f"{OPENWEATHER_BASE_URL}/weather"
            params = {
                'q': location,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Transform data to internal format
            if date:
                # Find the forecast for the specific date
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
                for item in data.get('list', []):
                    item_date = datetime.fromtimestamp(item['dt']).date()
                    if item_date == target_date:
                        weather_info = {
                            'temperature': round(item['main']['temp'], 1),
                            'humidity': round(item['main']['humidity']),
                            'wind_speed': round(item['wind']['speed'], 1),
                            'description': item['weather'][0]['description'],
                            'precipitation': round(item.get('rain', {}).get('3h', 0) / 3, 1) if 'rain' in item else 0.0,
                            'icon': item['weather'][0]['icon']
                        }
                        break
                else:
                    weather_info = {
                        'temperature': round(data['list'][0]['main']['temp'], 1),
                        'humidity': round(data['list'][0]['main']['humidity']),
                        'wind_speed': round(data['list'][0]['wind']['speed'], 1),
                        'description': data['list'][0]['weather'][0]['description'],
                        'precipitation': 0.0,
                        'icon': data['list'][0]['weather'][0]['icon']
                    }
            else:
                weather_info = {
                    'temperature': round(data['main']['temp'], 1),
                    'humidity': round(data['main']['humidity']),
                    'wind_speed': round(data['wind']['speed'], 1),
                    'description': data['weather'][0]['description'],
                    'precipitation': 0.0,
                    'icon': data['weather'][0]['icon']
                }
            
            # Cache the result
            weather_cache[cache_key] = {
                'data': weather_info,
                'timestamp': time.time()
            }
            
            return weather_info
        else:
            return None
            
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def calculate_suitability_score(event_type, weather_data):
    """Calculate weather suitability score for an event type using new algorithm"""
    if not weather_data or event_type not in EVENT_WEATHER_PREFERENCES:
        return {"score": 0, "rating": "Poor", "details": {}}
    
    prefs = EVENT_WEATHER_PREFERENCES[event_type]
    temp = weather_data['temperature']
    wind = weather_data['wind_speed']
    precip = weather_data['precipitation']
    humidity = weather_data.get('humidity', 50)  # Default if not available
    description = weather_data['description'].lower()
    
    score = 0
    details = {}
    
    # Convert wind from m/s to km/h for scoring
    wind_kmh = wind * 3.6
    
    if event_type == 'sports':
        # Sports Event Scoring
        # Temperature scoring
        temp_config = prefs['scoring']['temperature']
        if temp_config['ideal_range'][0] <= temp <= temp_config['ideal_range'][1]:
            temp_points = temp_config['max_points']
            temp_status = 'Ideal'
        elif temp_config['acceptable_range'][0] <= temp <= temp_config['acceptable_range'][1]:
            temp_points = temp_config['acceptable_points']
            temp_status = 'Acceptable'
        else:
            temp_points = 0
            temp_status = 'Poor'
        
        score += temp_points
        details['temperature'] = {
            'value': temp,
            'points': temp_points,
            'status': temp_status
        }
        
        # Precipitation scoring (convert mm to percentage chance)
        precip_chance = min(precip * 100, 100)  # Convert mm to percentage
        precip_config = prefs['scoring']['precipitation']
        if precip_chance <= precip_config['ideal_max']:
            precip_points = precip_config['max_points']
            precip_status = 'Ideal'
        elif precip_chance <= precip_config['acceptable_max']:
            precip_points = precip_config['acceptable_points']
            precip_status = 'Acceptable'
        else:
            precip_points = 0
            precip_status = 'Poor'
        
        score += precip_points
        details['precipitation'] = {
            'value': precip,
            'points': precip_points,
            'status': precip_status
        }
        
        # Wind scoring
        wind_config = prefs['scoring']['wind']
        if wind_kmh <= wind_config['ideal_max']:
            wind_points = wind_config['max_points']
            wind_status = 'Ideal'
        elif wind_kmh <= wind_config['acceptable_max']:
            wind_points = wind_config['acceptable_points']
            wind_status = 'Acceptable'
        else:
            wind_points = 0
            wind_status = 'Poor'
        
        score += wind_points
        details['wind'] = {
            'value': wind,
            'points': wind_points,
            'status': wind_status
        }
        
        # Conditions scoring
        conditions_config = prefs['scoring']['conditions']
        conditions_points = 0
        conditions_status = 'Poor'
        
        for condition, points in conditions_config['scores'].items():
            if condition in description:
                conditions_points = points
                conditions_status = condition.title()
                break
        
        score += conditions_points
        details['conditions'] = {
            'value': description,
            'points': conditions_points,
            'status': conditions_status
        }
        
    elif event_type == 'formal':
        # Formal Event Scoring
        # Precipitation scoring (highest priority)
        precip_chance = min(precip * 100, 100)
        precip_config = prefs['scoring']['precipitation']
        if precip_chance <= precip_config['ideal_max']:
            precip_points = precip_config['max_points']
            precip_status = 'Ideal'
        elif precip_chance <= precip_config['acceptable_max']:
            precip_points = precip_config['acceptable_points']
            precip_status = 'Acceptable'
        else:
            precip_points = 0
            precip_status = 'Poor'
        
        score += precip_points
        details['precipitation'] = {
            'value': precip,
            'points': precip_points,
            'status': precip_status
        }
        
        # Temperature scoring
        temp_config = prefs['scoring']['temperature']
        if temp_config['ideal_range'][0] <= temp <= temp_config['ideal_range'][1]:
            temp_points = temp_config['max_points']
            temp_status = 'Ideal'
        elif temp_config['acceptable_range'][0] <= temp <= temp_config['acceptable_range'][1]:
            temp_points = temp_config['acceptable_points']
            temp_status = 'Acceptable'
        else:
            temp_points = 0
            temp_status = 'Poor'
        
        score += temp_points
        details['temperature'] = {
            'value': temp,
            'points': temp_points,
            'status': temp_status
        }
        
        # Humidity scoring
        humidity_config = prefs['scoring']['humidity']
        if humidity_config['ideal_range'][0] <= humidity <= humidity_config['ideal_range'][1]:
            humidity_points = humidity_config['max_points']
            humidity_status = 'Ideal'
        elif humidity_config['acceptable_range'][0] <= humidity <= humidity_config['acceptable_range'][1]:
            humidity_points = humidity_config['acceptable_points']
            humidity_status = 'Acceptable'
        else:
            humidity_points = 0
            humidity_status = 'Poor'
        
        score += humidity_points
        details['humidity'] = {
            'value': humidity,
            'points': humidity_points,
            'status': humidity_status
        }
        
        # Wind scoring
        wind_config = prefs['scoring']['wind']
        if wind_kmh <= wind_config['ideal_max']:
            wind_points = wind_config['max_points']
            wind_status = 'Ideal'
        elif wind_kmh <= wind_config['acceptable_max']:
            wind_points = wind_config['acceptable_points']
            wind_status = 'Acceptable'
        else:
            wind_points = 0
            wind_status = 'Poor'
        
        score += wind_points
        details['wind'] = {
            'value': wind,
            'points': wind_points,
            'status': wind_status
        }
        
    elif event_type == 'adventure':
        # Outdoor Adventure Scoring
        # Temperature scoring
        temp_config = prefs['scoring']['temperature']
        if temp_config['ideal_range'][0] <= temp <= temp_config['ideal_range'][1]:
            temp_points = temp_config['max_points']
            temp_status = 'Ideal'
        elif temp_config['acceptable_range'][0] <= temp <= temp_config['acceptable_range'][1]:
            temp_points = temp_config['acceptable_points']
            temp_status = 'Acceptable'
        else:
            temp_points = 0
            temp_status = 'Poor'
        
        score += temp_points
        details['temperature'] = {
            'value': temp,
            'points': temp_points,
            'status': temp_status
        }
        
        # Precipitation scoring
        precip_chance = min(precip * 100, 100)
        precip_config = prefs['scoring']['precipitation']
        if precip_chance <= precip_config['ideal_max']:
            precip_points = precip_config['max_points']
            precip_status = 'Ideal'
        elif precip_chance <= precip_config['acceptable_max']:
            precip_points = precip_config['acceptable_points']
            precip_status = 'Acceptable'
        else:
            precip_points = 0
            precip_status = 'Poor'
        
        score += precip_points
        details['precipitation'] = {
            'value': precip,
            'points': precip_points,
            'status': precip_status
        }
        
        # Visibility scoring (estimated from weather conditions)
        visibility = 10  # Default good visibility
        if 'fog' in description or 'mist' in description:
            visibility = 2
        elif 'haze' in description:
            visibility = 5
        elif 'rain' in description or 'snow' in description:
            visibility = 7
        
        visibility_config = prefs['scoring']['visibility']
        if visibility >= visibility_config['ideal_min']:
            visibility_points = visibility_config['max_points']
            visibility_status = 'Ideal'
        elif visibility >= visibility_config['acceptable_min']:
            visibility_points = visibility_config['acceptable_points']
            visibility_status = 'Acceptable'
        else:
            visibility_points = 0
            visibility_status = 'Poor'
        
        score += visibility_points
        details['visibility'] = {
            'value': visibility,
            'points': visibility_points,
            'status': visibility_status
        }
        
        # Wind scoring
        wind_config = prefs['scoring']['wind']
        if wind_config['ideal_range'][0] <= wind_kmh <= wind_config['ideal_range'][1]:
            wind_points = wind_config['max_points']
            wind_status = 'Ideal'
        elif wind_config['acceptable_range'][0] <= wind_kmh <= wind_config['acceptable_range'][1]:
            wind_points = wind_config['acceptable_points']
            wind_status = 'Acceptable'
        else:
            wind_points = 0
            wind_status = 'Poor'
        
        score += wind_points
        details['wind'] = {
            'value': wind,
            'points': wind_points,
            'status': wind_status
        }
        
    elif event_type == 'picnic':
        # Family/Friends Picnic Scoring
        # Comfort scoring (temperature + humidity consideration)
        comfort_config = prefs['scoring']['comfort']
        if comfort_config['ideal_range'][0] <= temp <= comfort_config['ideal_range'][1]:
            comfort_points = comfort_config['max_points']
            comfort_status = 'Ideal'
        elif comfort_config['acceptable_range'][0] <= temp <= comfort_config['acceptable_range'][1]:
            comfort_points = comfort_config['acceptable_points']
            comfort_status = 'Acceptable'
        else:
            comfort_points = 0
            comfort_status = 'Poor'
        
        score += comfort_points
        details['comfort'] = {
            'value': temp,
            'points': comfort_points,
            'status': comfort_status
        }
        
        # Precipitation scoring
        precip_chance = min(precip * 100, 100)
        precip_config = prefs['scoring']['precipitation']
        if precip_chance <= precip_config['ideal_max']:
            precip_points = precip_config['max_points']
            precip_status = 'Ideal'
        elif precip_chance <= precip_config['acceptable_max']:
            precip_points = precip_config['acceptable_points']
            precip_status = 'Acceptable'
        else:
            precip_points = 0
            precip_status = 'Poor'
        
        score += precip_points
        details['precipitation'] = {
            'value': precip,
            'points': precip_points,
            'status': precip_status
        }
        
        # UV Index scoring (estimated from weather conditions)
        uv_index = 3  # Default moderate UV
        if 'clear' in description and 'sunny' in description:
            uv_index = 7
        elif 'clear' in description:
            uv_index = 5
        elif 'cloudy' in description or 'overcast' in description:
            uv_index = 2
        
        uv_config = prefs['scoring']['uv_index']
        if uv_index <= uv_config['ideal_max']:
            uv_points = uv_config['max_points']
            uv_status = 'Ideal'
        elif uv_index <= uv_config['acceptable_max']:
            uv_points = uv_config['acceptable_points']
            uv_status = 'Acceptable'
        else:
            uv_points = uv_config['high_points']
            uv_status = 'High'
        
        score += uv_points
        details['uv_index'] = {
            'value': uv_index,
            'points': uv_points,
            'status': uv_status
        }
        
        # Wind scoring
        wind_config = prefs['scoring']['wind']
        if wind_config['ideal_range'][0] <= wind_kmh <= wind_config['ideal_range'][1]:
            wind_points = wind_config['max_points']
            wind_status = 'Ideal'
        elif wind_config['acceptable_range'][0] <= wind_kmh <= wind_config['acceptable_range'][1]:
            wind_points = wind_config['acceptable_points']
            wind_status = 'Acceptable'
        else:
            wind_points = 0
            wind_status = 'Poor'
        
        score += wind_points
        details['wind'] = {
            'value': wind,
            'points': wind_points,
            'status': wind_status
        }
    
    # Convert score to rating
    max_score = prefs['total_max_score']
    percentage = (score / max_score) * 100
    
    if percentage >= 85:
        rating = "Good"
    elif percentage >= 65:
        rating = "Okay"
    else:
        rating = "Poor"
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": round(percentage, 1),
        "rating": rating,
        "details": details
    }

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    global event_counter
    
    try:
        data = request.get_json()
        required_fields = ['name', 'location', 'date', 'event_type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        event_id = event_counter
        event_counter += 1
        
        event = {
            'id': event_id,
            'name': data['name'],
            'location': data['location'],
            'date': data['date'],
            'event_type': data['event_type'],
            'created_at': datetime.now().isoformat()
        }
        
        events[event_id] = event
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def list_events():
    """List all events with basic weather info and suitability scores"""
    try:
        events_list = []
        for event in events.values():
            # Get basic weather info
            weather_data = get_weather_data(event['location'], event['date'])
            event_with_weather = event.copy()
            
            if weather_data:
                event_with_weather['weather'] = {
                    'temperature': weather_data['temperature'],
                    'description': weather_data['description'],
                    'icon': weather_data['icon']
                }
                # Calculate suitability score
                suitability = calculate_suitability_score(event['event_type'], weather_data)
                event_with_weather['suitability'] = suitability
            else:
                event_with_weather['weather'] = None
                event_with_weather['suitability'] = {
                    "score": 0,
                    "max_score": 100,
                    "percentage": 0,
                    "rating": "Unknown",
                    "details": {}
                }
            
            events_list.append(event_with_weather)
        
        return jsonify({
            'events': events_list,
            'count': len(events_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an event's details"""
    try:
        if event_id not in events:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        event = events[event_id]
        
        # Update allowed fields
        allowed_fields = ['name', 'location', 'date', 'event_type']
        for field in allowed_fields:
            if field in data:
                event[field] = data[field]
        
        event['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': event
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        if event_id not in events:
            return jsonify({'error': 'Event not found'}), 404
        
        deleted_event = events.pop(event_id)
        
        return jsonify({
            'message': 'Event deleted successfully',
            'event': deleted_event
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<location>/<date>', methods=['GET'])
def get_weather(location, date):
    """Fetch and show weather data for a location and date"""
    try:
        weather_data = get_weather_data(location, date)
        
        if weather_data:
            return jsonify({
                'location': location,
                'date': date,
                'weather': weather_data
            })
        else:
            return jsonify({'error': 'Unable to fetch weather data'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>/suitability', methods=['GET'])
def get_suitability(event_id):
    """Return a suitability score with detailed breakdown"""
    try:
        if event_id not in events:
            return jsonify({'error': 'Event not found'}), 404
        
        event = events[event_id]
        weather_data = get_weather_data(event['location'], event['date'])
        
        if not weather_data:
            return jsonify({'error': 'Unable to fetch weather data'}), 500
        
        suitability = calculate_suitability_score(event['event_type'], weather_data)
        
        return jsonify({
            'event': event,
            'weather': weather_data,
            'suitability': suitability
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<int:event_id>/alternatives', methods=['GET'])
def get_alternatives(event_id):
    """Suggest alternative dates within the same week if current weather is poor"""
    try:
        if event_id not in events:
            return jsonify({'error': 'Event not found'}), 404
        
        event = events[event_id]
        current_weather = get_weather_data(event['location'], event['date'])
        
        if not current_weather:
            return jsonify({'error': 'Unable to fetch weather data'}), 500
        
        current_suitability = calculate_suitability_score(event['event_type'], current_weather)
        
        alternatives = []
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        
        # Check dates within the same week
        for i in range(-3, 4):  # 3 days before and after
            if i == 0:  # Skip current date
                continue
                
            alternative_date = event_date + timedelta(days=i)
            alternative_date_str = alternative_date.strftime('%Y-%m-%d')
            
            weather_data = get_weather_data(event['location'], alternative_date_str)
            if weather_data:
                suitability = calculate_suitability_score(event['event_type'], weather_data)
                alternatives.append({
                    'date': alternative_date_str,
                    'weather': weather_data,
                    'suitability': suitability
                })
        
        # Sort alternatives by suitability score (highest first)
        alternatives.sort(key=lambda x: x['suitability']['score'], reverse=True)
        
        return jsonify({
            'event': event,
            'current_weather': current_weather,
            'current_suitability': current_suitability,
            'alternatives': alternatives[:5]  # Return top 5 alternatives
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'events_count': len(events)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000))) 