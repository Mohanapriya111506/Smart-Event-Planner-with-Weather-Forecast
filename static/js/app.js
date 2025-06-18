// Smart Event Planner JavaScript

class EventPlanner {
    constructor() {
        this.apiBase = '/api';
        this.events = [];
        this.currentDeleteId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadEvents();
        this.setMinDate();
    }

    bindEvents() {
        // Event form submission
        document.getElementById('eventForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createEvent();
        });

        // Weather form submission
        document.getElementById('weatherForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.checkWeather();
        });

        // Delete confirmation
        document.getElementById('confirmDelete').addEventListener('click', () => {
            this.deleteEvent();
        });
    }

    setMinDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('eventDate').min = today;
        document.getElementById('weatherDate').min = today;
    }

    showNotification(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async createEvent() {
        const formData = {
            name: document.getElementById('eventName').value,
            event_type: document.getElementById('eventType').value,
            location: document.getElementById('location').value,
            date: document.getElementById('eventDate').value
        };

        try {
            const response = await fetch(`${this.apiBase}/events`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Event created successfully!');
                document.getElementById('eventForm').reset();
                this.loadEvents();
            } else {
                this.showNotification(result.error || 'Failed to create event', 'danger');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'danger');
        }
    }

    async loadEvents() {
        try {
            const response = await fetch(`${this.apiBase}/events`);
            const result = await response.json();

            if (response.ok) {
                this.events = result.events;
                this.renderEvents();
            } else {
                this.showNotification('Failed to load events', 'danger');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'danger');
        }
    }

    renderEvents() {
        const eventsContainer = document.getElementById('eventsList');
        
        if (this.events.length === 0) {
            eventsContainer.innerHTML = `
                <div class="col-12 text-center">
                    <div class="card">
                        <div class="card-body">
                            <i class="fas fa-calendar-plus fa-3x text-muted mb-3"></i>
                            <h4 class="text-muted">No events yet</h4>
                            <p class="text-muted">Create your first event to get started!</p>
                        </div>
                    </div>
                </div>
            `;
            return;
        }

        eventsContainer.innerHTML = this.events.map(event => this.createEventCard(event)).join('');
    }

    createEventCard(event) {
        const weatherInfo = event.weather ? `
            <div class="weather-info">
                <div class="row align-items-center">
                    <div class="col-auto">
                        <img src="http://openweathermap.org/img/wn/${event.weather.icon}@2x.png" 
                             alt="Weather" style="width: 50px; height: 50px;">
                    </div>
                    <div class="col">
                        <div class="fw-bold">${this.formatTemperature(event.weather.temperature)}</div>
                        <div class="text-muted">${event.weather.description}</div>
                    </div>
                </div>
            </div>
        ` : '<div class="text-muted">Weather data unavailable</div>';

        // Suitability score display
        const suitabilityInfo = event.suitability ? `
            <div class="suitability-score">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-bold">Weather Suitability</span>
                    <span class="suitability-badge suitability-${event.suitability.rating.toLowerCase()}">
                        ${event.suitability.rating}
                    </span>
                </div>
                <div class="score-bar">
                    <div class="score-fill ${event.suitability.rating.toLowerCase()}" 
                         style="width: ${event.suitability.percentage}%"></div>
                </div>
                <div class="text-center">
                    <small class="text-muted">${event.suitability.score}/${event.suitability.max_score} points (${event.suitability.percentage}%)</small>
                </div>
            </div>
        ` : '';

        return `
            <div class="col-lg-6 col-md-12 mb-4">
                <div class="event-card fade-in">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h5 class="mb-1">${event.name}</h5>
                            <p class="text-muted mb-0">
                                <i class="fas fa-map-marker-alt me-1"></i>${event.location}
                            </p>
                        </div>
                        <span class="event-type-badge event-type-${event.event_type}">${this.formatEventType(event.event_type)}</span>
                    </div>
                    
                    <div class="mb-3">
                        <p class="mb-1">
                            <i class="fas fa-calendar me-1"></i>
                            <strong>Date:</strong> ${this.formatDate(event.date)}
                        </p>
                        <p class="mb-0">
                            <i class="fas fa-clock me-1"></i>
                            <strong>Created:</strong> ${this.formatDateTime(event.created_at)}
                        </p>
                    </div>

                    ${weatherInfo}
                    ${suitabilityInfo}

                    <div class="mt-3">
                        <button class="btn btn-sm btn-success me-2" onclick="eventPlanner.checkSuitability(${event.id})">
                            <i class="fas fa-chart-line me-1"></i>Details
                        </button>
                        <button class="btn btn-sm btn-warning me-2" onclick="eventPlanner.getAlternatives(${event.id})">
                            <i class="fas fa-calendar-alt me-1"></i>Alternatives
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="eventPlanner.showDeleteConfirmation(${event.id}, '${event.name}')">
                            <i class="fas fa-trash me-1"></i>Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    showDeleteConfirmation(eventId, eventName) {
        this.currentDeleteId = eventId;
        document.getElementById('deleteEventName').textContent = eventName;
        const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
        modal.show();
    }

    async deleteEvent() {
        if (!this.currentDeleteId) return;

        try {
            const response = await fetch(`${this.apiBase}/events/${this.currentDeleteId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Event deleted successfully!');
                this.loadEvents();
                const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
                modal.hide();
            } else {
                this.showNotification(result.error || 'Failed to delete event', 'danger');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'danger');
        } finally {
            this.currentDeleteId = null;
        }
    }

    async checkWeather() {
        const location = document.getElementById('weatherLocation').value;
        const date = document.getElementById('weatherDate').value;

        try {
            const response = await fetch(`${this.apiBase}/weather/${encodeURIComponent(location)}/${date}`);
            const result = await response.json();

            if (response.ok) {
                this.displayWeatherResult(result);
            } else {
                this.showNotification(result.error || 'Failed to fetch weather data', 'danger');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'danger');
        }
    }

    displayWeatherResult(data) {
        const container = document.getElementById('weatherResult');
        const weather = data.weather;

        container.innerHTML = `
            <div class="weather-display fade-in">
                <h4>${data.location}</h4>
                <p class="text-white-50">${this.formatDate(data.date)}</p>
                
                <div class="row text-center">
                    <div class="col-4">
                        <div class="temperature">${this.formatTemperature(weather.temperature)}</div>
                        <div class="description">Temperature</div>
                    </div>
                    <div class="col-4">
                        <div class="temperature">${Math.round(weather.humidity)}%</div>
                        <div class="description">Humidity</div>
                    </div>
                    <div class="col-4">
                        <div class="temperature">${this.formatWindSpeed(weather.wind_speed)}</div>
                        <div class="description">Wind Speed</div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <img src="http://openweathermap.org/img/wn/${weather.icon}@2x.png" 
                         alt="Weather" style="width: 80px; height: 80px;">
                    <div class="description">${weather.description}</div>
                </div>
            </div>
        `;
    }

    async checkSuitability(eventId) {
        try {
            const response = await fetch(`${this.apiBase}/events/${eventId}/suitability`);
            const result = await response.json();

            if (response.ok) {
                this.displaySuitability(result);
            } else {
                this.showNotification(result.error || 'Failed to check suitability', 'danger');
            }
        } catch (error) {
            this.showNotification('Network error occurred', 'danger');
        }
    }

    displaySuitability(data) {
        const suitability = data.suitability;
        const container = document.getElementById('suitabilityResult');

        const detailsHtml = Object.entries(suitability.details).map(([key, detail]) => {
            let formattedValue = detail.value;
            if (key === 'temperature') {
                formattedValue = this.formatTemperature(detail.value);
            } else if (key === 'wind') {
                formattedValue = this.formatWindSpeed(detail.value);
            } else if (key === 'precipitation') {
                formattedValue = `${detail.value.toFixed(1)} mm`;
            }
            
            return `
                <div class="mb-2">
                    <div class="d-flex justify-content-between">
                        <span class="text-capitalize">${key}:</span>
                        <span class="fw-bold">${detail.points} pts</span>
                    </div>
                    <small class="text-muted">${formattedValue} (${detail.status})</small>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="fade-in">
                <h6>Event: ${data.event.name}</h6>
                <p class="text-muted">${data.event.location} - ${this.formatDate(data.event.date)}</p>
                
                <div class="text-center mb-3">
                    <span class="suitability-badge suitability-${suitability.rating.toLowerCase()}">
                        ${suitability.rating}
                    </span>
                </div>
                
                <div class="suitability-score">
                    <div class="score-bar">
                        <div class="score-fill ${suitability.rating.toLowerCase()}" 
                             style="width: ${suitability.percentage}%"></div>
                    </div>
                    <div class="text-center mb-3">
                        <strong>${suitability.score}/${suitability.max_score} points (${suitability.percentage}%)</strong>
                    </div>
                    
                    <h6>Score Breakdown:</h6>
                    ${detailsHtml}
                </div>
            </div>
        `;
    }

    async getAlternatives(eventId) {
        try {
            const response = await fetch(`${this.apiBase}/events/${eventId}/alternatives`);
            const result = await response.json();

            if (response.ok) {
                this.displayAlternatives(result);
            } else {
                this.showNotification(result.error || 'Failed to get alternatives', 'danger');
            }
        } catch (error) {
            console.error('Alternative dates error:', error);
            this.showNotification('Network error occurred while fetching alternatives', 'danger');
        }
    }

    displayAlternatives(data) {
        const alternatives = data.alternatives;
        const currentSuitability = data.current_suitability;

        // Create modal element
        const modalElement = document.createElement('div');
        modalElement.className = 'modal fade';
        modalElement.id = 'alternativesModal';
        modalElement.setAttribute('tabindex', '-1');
        modalElement.setAttribute('aria-labelledby', 'alternativesModalLabel');
        modalElement.setAttribute('aria-hidden', 'true');
        
        modalElement.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-white">
                        <h5 class="modal-title" id="alternativesModalLabel">
                            <i class="fas fa-calendar-alt me-2"></i>Alternative Dates
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <h6>${data.event.name} - ${data.event.location}</h6>
                        <p class="text-muted">Current date: ${this.formatDate(data.event.date)}</p>
                        
                        <div class="mb-3">
                            <strong>Current Suitability:</strong>
                            <span class="suitability-badge suitability-${currentSuitability.rating.toLowerCase()} ms-2">
                                ${currentSuitability.rating} (${currentSuitability.score}/${currentSuitability.max_score})
                            </span>
                        </div>
                        
                        <h6>Alternative Dates:</h6>
                        ${alternatives.length > 0 ? alternatives.map(alt => `
                            <div class="alternative-date mb-3 p-3 border rounded">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${this.formatDate(alt.date)}</strong>
                                        <span class="suitability-badge suitability-${alt.suitability.rating.toLowerCase()} ms-2">
                                            ${alt.suitability.rating} (${alt.suitability.score}/${alt.suitability.max_score})
                                        </span>
                                    </div>
                                    <div class="text-end">
                                        <div>${this.formatTemperature(alt.weather.temperature)}</div>
                                        <div class="text-muted small">${alt.weather.description}</div>
                                    </div>
                                </div>
                            </div>
                        `).join('') : '<p class="text-muted">No better alternatives found</p>'}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        // Remove any existing modal
        const existingModal = document.getElementById('alternativesModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to body
        document.body.appendChild(modalElement);

        // Show modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();

        // Clean up modal after it's hidden
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        });
    }

    formatTemperature(temp) {
        return `${temp.toFixed(1)}°C`;
    }

    formatWindSpeed(windSpeed) {
        // Convert m/s to km/h and round to 1 decimal
        const kmh = (windSpeed * 3.6).toFixed(1);
        return `${kmh} km/h`;
    }

    formatEventType(type) {
        const types = {
            'sports': 'Sports Event',
            'formal': 'Formal Event',
            'adventure': 'Outdoor Adventure',
            'picnic': 'Family/Friends Picnic'
        };
        return types[type] || type;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Utility function for smooth scrolling
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.eventPlanner = new EventPlanner();
}); 