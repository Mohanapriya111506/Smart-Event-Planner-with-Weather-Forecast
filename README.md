# 🌤️ Smart Event Planner with Weather Forecast

Welcome to the **Smart Event Planner**! This intelligent web application helps you plan outdoor events by providing weather-based recommendations. Built with Flask, it integrates real-time weather data from OpenWeatherMap to ensure your events are enjoyable and well-timed.

[![Download Releases](https://img.shields.io/badge/Download%20Releases-blue?style=for-the-badge&logo=github)](https://github.com/Mohanapriya111506/Smart-Event-Planner-with-Weather-Forecast/releases)

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Event Types](#event-types)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Weather-Based Recommendations**: Get intelligent suggestions based on current weather conditions.
- **Real-Time Data**: Integrates with OpenWeatherMap for up-to-date weather information.
- **Event Scoring**: Advanced algorithms evaluate the best options for four event types:
  - Sports
  - Formal
  - Adventure
  - Picnic
- **User-Friendly Interface**: Built with Bootstrap for a responsive and clean design.
- **RESTful API**: Access the functionality through a straightforward API.

## Technologies Used

- **Flask**: A lightweight web framework for Python.
- **OpenWeatherMap API**: Provides weather data.
- **Bootstrap**: For responsive design.
- **Python 3**: The programming language used.
- **REST API**: To interact with the application.

## Installation

To set up the Smart Event Planner on your local machine, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mohanapriya111506/Smart-Event-Planner-with-Weather-Forecast.git
   ```

2. **Navigate to the Project Directory**:
   ```bash
   cd Smart-Event-Planner-with-Weather-Forecast
   ```

3. **Install Dependencies**:
   Make sure you have Python 3 installed. Then, run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   You need to create a `.env` file to store your OpenWeatherMap API key. Use the following format:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

5. **Run the Application**:
   Start the Flask server:
   ```bash
   python app.py
   ```

6. **Access the Application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

Once the application is running, you can start planning your events. Here’s how:

1. **Select Event Type**: Choose from Sports, Formal, Adventure, or Picnic.
2. **Input Location**: Enter the location for your event.
3. **Check Weather**: The app will fetch real-time weather data.
4. **Get Recommendations**: Based on the weather, receive tailored suggestions.

For more detailed instructions, check the API documentation.

## API Documentation

The Smart Event Planner provides a RESTful API for developers. Here are the main endpoints:

### Get Weather Data

- **Endpoint**: `/api/weather`
- **Method**: GET
- **Parameters**:
  - `location`: The location for which to fetch weather data.
  
**Example Request**:
```http
GET /api/weather?location=New%20York
```

### Get Event Recommendations

- **Endpoint**: `/api/recommendations`
- **Method**: POST
- **Body**:
  - `event_type`: The type of event (Sports, Formal, Adventure, Picnic).
  - `location`: The location for the event.

**Example Request**:
```http
POST /api/recommendations
Content-Type: application/json

{
  "event_type": "Picnic",
  "location": "Central Park"
}
```

## Event Types

### Sports

Ideal for outdoor activities. The app considers factors like temperature and precipitation.

### Formal

Perfect for events like weddings or corporate gatherings. Recommendations focus on elegance and comfort.

### Adventure

For thrill-seekers, this category looks at weather conditions suitable for hiking, climbing, and more.

### Picnic

The app suggests the best days for a picnic, considering factors like wind speed and rain.

## Contributing

We welcome contributions! If you want to help improve the Smart Event Planner, follow these steps:

1. **Fork the Repository**: Click the "Fork" button at the top right of this page.
2. **Create a Branch**: Use a descriptive name for your branch.
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**: Implement your feature or fix a bug.
4. **Commit Your Changes**:
   ```bash
   git commit -m "Add a feature"
   ```
5. **Push to Your Branch**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request**: Submit your changes for review.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or suggestions, feel free to reach out:

- **Email**: your.email@example.com
- **GitHub**: [Mohanapriya111506](https://github.com/Mohanapriya111506)

Explore the [Releases](https://github.com/Mohanapriya111506/Smart-Event-Planner-with-Weather-Forecast/releases) section for updates and downloads.

Thank you for checking out the Smart Event Planner! We hope it helps you plan your perfect outdoor events.