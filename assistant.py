import pywhatkit
import pyttsx3
import json
import csv
import speech_recognition as sr
from datetime import datetime, date, timezone as dt_timezone
import requests
from timezonefinder import TimezoneFinder
from pytz import timezone
import sys
from dotenv import load_dotenv
import os

load_dotenv()

engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
engine.setProperty('rate', 160)

TODO_FILE = "todo_data.json"

def init_todo_file():
    try:
        with open(TODO_FILE, "r") as f:
            json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(TODO_FILE, "w") as f:
            json.dump([], f)

def menu():
    while True:
        print("\nWhat would you like me to do : ")
        print("1. Find out current date")
        print("2. Find out current time in any city")
        print("3. Find out weather in any city")
        print("4. Play songs from YouTube")
        print("5. Search anything on Google")
        print("6. Add Todo list item")
        print("7. Export todo list to a file")
        print("8. Credits")
        print("9. Exit the program")
        print("Enter a number from 1-9 as your choice")

        try:
            ch = int(input(" "))
        except:
            print("Invalid input. Try again.")
            continue

        if ch == 1:
            date_today()
        elif ch == 2:
            cityname = input("Please enter city name: ")
            global_time(cityname)
        elif ch == 3:
            cityname = input("Please enter city name: ")
            weather(cityname)
        elif ch == 4:
            songname = input("Enter song name: ")
            pywhatkit.playonyt(songname)
        elif ch == 5:
            searchstring = input("Enter what you want to search: ")
            search(searchstring)
        elif ch == 6:
            todo()
        elif ch == 7:
            transfertasktofile()
        elif ch == 8:
            credits()
        elif ch == 9:
            sys.exit()
        else:
            print("Invalid option. Try again.")

        input("\nPress Enter to go back to the menu...")

def date_today():
    tdate = datetime.now()
    formatdate = f"The day is the {tdate.strftime('%d')}th of {tdate.strftime('%B')}, {tdate.strftime('%Y')}"
    print(formatdate)
    engine.say(formatdate)
    engine.runAndWait()

def say_time(timezonecity='Asia/Kolkata', citytimename='Mumbai'):

    try:
        city_time = datetime.now(timezone(timezonecity))
        formattime = f"The time in {citytimename} is {city_time.strftime('%I:%M %p')}"
        print(formattime)
        engine.say(formattime)
        engine.runAndWait()
    except Exception as e:
        print("Error getting or speaking time:", e)
        engine.say("Sorry, I couldn't get the time for that city.")
        engine.runAndWait()

def search(searchstring='Latest news'):
    pywhatkit.search(searchstring)

def hear():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            engine.say("Hi I am Hope, your virtual assistant. What would you like me to do?")
            engine.runAndWait()
            print("\nListening for command...")
            print("Say: date, time, weather, play <song>, search, to do, export, credits, exit")
            audio = r.listen(source)
            text = r.recognize_google(audio, language='en-IN').lower()
            print(f"You said: {text}")

            if 'play' in text:
                song = text.replace('play', '')
                print('Playing - ' + song)
                engine.say('Playing ' + song)
                engine.runAndWait()
                pywhatkit.playonyt(song)
            elif 'weather' in text:
                print("Say the city name:")
                city = r.recognize_google(r.listen(source), language='en-IN')
                weather(city)
            elif 'time' in text:
                print("Say the city name:")
                city = r.recognize_google(r.listen(source), language='en-IN')
                global_time(city)
            elif 'search' in text:
                print("Say what you want to search:")
                search_term = r.recognize_google(r.listen(source), language='en-IN')
                search(search_term)
            elif 'date' in text:
                date_today()
            elif 'to do' in text:
                todo()
            elif 'export' in text:
                transfertasktofile()
            elif 'credits' in text:
                credits()
            elif 'exit' in text:
                engine.say("Goodbye")
                engine.runAndWait()
                sys.exit()
            else:
                print("Sorry, I didn't get that.")

            input("\nPress Enter to go back to listening...")

def weather(cname):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"{base_url}appid={api_key}&q={cname}"
    response = requests.get(url).json()

    def kelvintocelsius(k):
        return k - 273.15

    if response.get("cod") != 200:
        print("City not found or API issue.")
        return

    temp_c = kelvintocelsius(response['main']['temp'])
    humidity = response['main']['humidity']
    wind_speed = response['wind']['speed']
    description = response['weather'][0]['description']

    offset = response['timezone']
    sunrise_time = datetime.fromtimestamp(response['sys']['sunrise'] + offset, tz=dt_timezone.utc).astimezone()
    sunset_time = datetime.fromtimestamp(response['sys']['sunset'] + offset, tz=dt_timezone.utc).astimezone()

    data = [
        f"Temperature in {cname}: {temp_c:.2f}°C",
        f"Humidity in {cname}: {humidity}%",
        f"Wind speed in {cname}: {wind_speed} m/s",
        f"General weather in {cname}: {description}",
        f"Sun rises at {sunrise_time.strftime('%H:%M:%S')}",
        f"Sun sets at {sunset_time.strftime('%H:%M:%S')}"
    ]

    for line in data:
        print(line)
        engine.say(line)

    engine.runAndWait()

def get_coords_from_file(cityname):
    try:
        with open("cities.json", "r") as f:
            cities = json.load(f)
        return cities.get(cityname.lower())
    except FileNotFoundError:
        print("cities.json not found.")
        return None

def global_time(citynametime):
    coords = get_coords_from_file(citynametime)
    if not coords:
        print(f"City '{citynametime}' not found in offline database.")
        print("Please enter latitude and longitude manually.")
        global_time_manual()
        return

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=coords[0], lng=coords[1])

    if timezone_str:
        say_time(timezone_str, citynametime)
    else:
        print("Could not determine timezone.")

def global_time_manual():
    try:
        lat = float(input("Latitude: "))
        lng = float(input("Longitude: "))
    except ValueError:
        print("Invalid coordinates.")
        return

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat, lng=lng)

    if timezone_str:
        say_time(timezone_str, f"{lat}, {lng}")
    else:
        print("Could not determine timezone.")

def todo():
    init_todo_file()
    print("What task is to be added?")
    engine.say("What task is to be added?")
    engine.runAndWait()

    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        desc = r.recognize_google(audio, language='en-IN')
        print(f"Task: {desc}")

    with open(TODO_FILE, "r") as f:
        data = json.load(f)

    sr_no = max([item["SrNo"] for item in data], default=0) + 1
    new_task = {
        "SrNo": sr_no,
        "Date": str(date.today()),
        "Description": desc,
        "Status": "Pending"
    }

    data.append(new_task)
    with open(TODO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def transfertasktofile():
    engine.say("Starting to export tasks.")
    engine.runAndWait()

    init_todo_file()
    with open(TODO_FILE, "r") as f:
        data = json.load(f)

    filename = f"task_{date.today()}.csv"
    with open(filename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["SrNo", "Date", "Description", "Status"])
        writer.writeheader()
        writer.writerows(data)

    engine.say("Finished exporting.")
    engine.runAndWait()
    print("Exported to", filename)

def credits():
    print("\nCreated by Karan R.")
    engine.say("This program was created by Karan.")
    engine.runAndWait()



print("Please select your mode:")
print("1: Voice Commands")
print("2: Text Menu")
try:
    choice = int(input("Enter 1 or 2: "))
except:
    choice = 2

if choice == 1:
    hear()
elif choice == 2:
    menu()
else:
    print("Oops... Wrong option. Exiting...")
