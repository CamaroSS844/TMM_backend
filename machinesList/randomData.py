# {
#     "id": 1,
#     "shift_number": 1,
#     "date": "2020-12-15",
#     "distance_travelled": 235,
#     "tonnage": "34",
#     "fuel_consumed": 200,
#     "no_of_loads": 20,
#     "operating_hours": 30,
#     "idle_hours": 34,
#     "engine_hours": 50,
#     "transmission_hours": 25,
#     "mine": 1
# }

import random
import requests
import json
from datetime import datetime, timedelta

data = []
shift_number =  1


# Initialize the global date
current_date = datetime(2024, 1, 1)  # Replace with the starting date
store = ""

def increment_date(shift_number):
    global current_date
    global store
    if (shift_number == 1):
        current_date += timedelta(days=1)  # Increment the date by one day

        # Convert to string
        dt_string = current_date.strftime('%Y-%m-%d %H:%M:%S')
        dt_string = dt_string.split(" ")[0]
        return dt_string  # Return the updated date
    else :
        dt_string = current_date.strftime('%Y-%m-%d %H:%M:%S')
        dt_string = dt_string.split(" ")[0]
        return dt_string

        


def randomData(number):
    server_url = "http://127.0.0.1:8000/machines/opsum/"
    global data
    for i in range(number):
        global data 
        global shift_number
        global current_date
        shift_number = 1 if (shift_number == 2) else 2
        date = increment_date(shift_number) 
        distance_travelled = random.randrange(0, 20)
        no_of_loads = 0 if (distance_travelled <= 3) else int((distance_travelled/20)* 50)
        tonnage = int(no_of_loads * random.randrange(6, 8))
        fuel_consumed = int(distance_travelled * random.randrange(8, 11))
        operating_hours =  int((distance_travelled/20)*7)
        idle_hours = int(operating_hours * 0.25)
        engine_hours = int(operating_hours * 0.75)

        data = [
            *data, 
                {
                    "shift_number": shift_number,
                    "date": date,
                    "distance_travelled": distance_travelled,
                    "tonnage": tonnage,
                    "fuel_consumed": fuel_consumed,
                    "no_of_loads": no_of_loads,
                    "operating_hours": operating_hours,
                    "idle_hours": idle_hours,
                    "engine_hours": engine_hours,
                    "transmission_hours": engine_hours,
                    "mine": 1,
                    "machine": 3,
                }
            ]
    
    try:
        response = requests.post(server_url, json=data)
        if response.status_code == 200 :
            print("Data posted successfully!")
        else:
            print(f"Failed to post data: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")


randomData(200)