## Python Voice Assistant (Hope)

A very simple Python-based command line voice assistant that can report time, weather, search the web, manage a to-do list, and more. Worked on it a couple of years back and found it again, so decided to upload it.

### Features
- Voice recognition (speech-to-text)
- Text-to-speech replies using pyttsx3
- Fetch weather data from OpenWeatherMap
- Play YouTube songs using pywhatkit
- Create and export a todo list
- Ask for time in any city via offline coordinates

### Setup

1. Clone the repo
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt

3. This project uses the OpenWeatherMap API to fetch weather data.

    Go to https://openweathermap.org/api

    Sign up and get your free API key

    Create a .env file in the project root with the following content:

   WEATHER_API_KEY=your_openweathermap_api_key_here
