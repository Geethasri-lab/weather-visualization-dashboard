from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# -----------------------------
# CONFIGURATION
# -----------------------------
API_KEY = "cf26a9807c1e8ba0a55cb923f9fed44c"  # 🔑 Replace this with your correct key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
IMG_PATH = "static/charts"

if not os.path.exists(IMG_PATH):
    os.makedirs(IMG_PATH)


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    cities = []
    weather_data = []

    if request.method == "POST":
        city_input = request.form["cities"]
        cities = [c.strip() for c in city_input.split(",") if c.strip()]

        for city in cities:
            params = {"q": city, "appid": API_KEY, "units": "metric"}
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            # Debugging line to check what's coming from API
            print(f"\n🔍 Response for {city}: {data}\n")

            if response.status_code == 200 and "main" in data:
                city_data = {
                    "City": city,
                    "Temperature": data["main"]["temp"],
                    "Humidity": data["main"]["humidity"],
                    "Pressure": data["main"]["pressure"],
                }
                weather_data.append(city_data)
            else:
                # Log the error message
                print(f"⚠️ Error fetching data for {city}: {data.get('message', 'Unknown error')}")
                weather_data.append({
                    "City": city,
                    "Temperature": None,
                    "Humidity": None,
                    "Pressure": None
                })

        # Generate charts if any valid data exists
        if any(d["Temperature"] is not None for d in weather_data):
            generate_charts(weather_data)

    return render_template("index.html", weather_data=weather_data, cities=cities)


# -----------------------------
# FUNCTION: Generate Charts
# -----------------------------
def generate_charts(weather_data):
    cities = [d["City"] for d in weather_data if d["Temperature"] is not None]
    temps = [d["Temperature"] for d in weather_data if d["Temperature"] is not None]
    humidity = [d["Humidity"] for d in weather_data if d["Humidity"] is not None]
    pressure = [d["Pressure"] for d in weather_data if d["Pressure"] is not None]

    if not cities:
        print("⚠️ No valid weather data to visualize.")
        return

    # Temperature Bar Chart
    plt.figure(figsize=(8, 5))
    plt.bar(cities, temps, color="skyblue")
    plt.title("Temperature (°C)")
    plt.ylabel("Temperature (°C)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{IMG_PATH}/temperature.png")
    plt.close()

    # Humidity Line Chart
    plt.figure(figsize=(8, 5))
    plt.plot(cities, humidity, marker="o", color="green")
    plt.title("Humidity (%)")
    plt.ylabel("Humidity (%)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{IMG_PATH}/humidity.png")
    plt.close()

    # Pressure Bar Chart
    plt.figure(figsize=(8, 5))
    plt.bar(cities, pressure, color="orange")
    plt.title("Pressure (hPa)")
    plt.ylabel("Pressure (hPa)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{IMG_PATH}/pressure.png")
    plt.close()


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
