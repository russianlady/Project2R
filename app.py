from flask import Flask, render_template, request
import requests

app = Flask(__name__)

api_key = 'your_api'# введите свой ключ


@app.route('/')
def index():
    return render_template('site.html') # выводим первую страничку


@app.route('/get_weather', methods=['POST'])
def get_weather():
    try:
        start_city = request.form['start_city']
        end_city = request.form['end_city']

        start_weather = get_weather_data(start_city) # данные о погоде в первом городе
        end_weather = get_weather_data(end_city) # данные о погоде во втором городе

        start_condition = check_bad_weather(start_weather) # получаем оценку погоды в первом городе
        end_condition = check_bad_weather(end_weather) # получаем оценку погоды во втором городе

        return render_template('site2.html', start_city=start_city, end_city=end_city, # выводим второую страничку
                               start_condition=start_condition, end_condition=end_condition)
    except Exception as e:
        return f"Произошла ошибка: {str(e)}" # выводим сообщение на случай ошибки


def get_weather_data(city):
    location_url = f"https://dataservice.accuweather.com/locations/v1/search?q={city}&apikey={api_key}"
    location_response = requests.get(location_url)
    location_data = location_response.json() # получаем данные о городе

    if not location_data:
        raise Exception(f"Город {city} не найден") # сообщение на случай ошибки

    location_key = location_data[0]['Key'] # получаем ключ города
    weather_url = f"https://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={api_key}&details=true"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json() # получаем данные о погоде

    if not weather_data:
        raise Exception(f"Не удалось получить данные о погоде для города {city}") # сообщение на случай ошибки

    return weather_data[0]  # возвращаем первый объект с погодой

def check_bad_weather(weather_data):
    temp = weather_data.get("Temperature", {}).get("Metric", {}).get("Value", None) #  получаем температуру
    wind_speed = weather_data.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value", None) # получаем скорость ветра
    rain_chance = weather_data.get("PrecipitationSummary", {}).get("Precipitation", {}).get("Value", None) # получаем вероятность дождя
    humidity = weather_data.get("RelativeHumidity", None) # получаем влажность


    if temp is None or wind_speed is None or rain_chance is None:
        return 'Ошибка в данных о погоде' # сообщение на случай ошибки

    # проверяем погоду на "хорошесть"
    if temp < -5:
        return 'Плохая погода: слишком холодно 0--0'
    elif temp > 33:
        return 'Плохая погода: слишком жарко 0.0'
    elif wind_speed > 50:
        return 'Плохая погода: сильный ветер 0_0'
    elif rain_chance > 80:
        return 'Плохая погода: вероятность дождя более 80% 0-0'
    else:
        return 'Погода хорошая ^.^'


if __name__ == '__main__':
    app.run(debug=True)
