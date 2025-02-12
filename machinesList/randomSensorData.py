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
    server_url = "http://127.0.0.1:8000/machines/sensorData/?date=all&machineID=1"
    global data

    for i in range(number):
        global data 
        global shift_number
        global current_date
        shift_number = 1 if (shift_number == 2) else 2
        date = increment_date(shift_number)

        data = [
            *data, 
                {
                    "date": date,
                    "shift_number": shift_number,
                    "mine": 1,
                    "machine": 1,
                    "BW1_FL_Brake_Wear": random.randrange(0, 50),
                    "BW2_FR_Brake_Wear": random.randrange(0, 50),
                    "BW3_RL_Brake_Wear": random.randrange(0, 50),
                    "BW4_RR_Brake_Wear": random.randrange(0, 50),
                    "BT1_FL_Brake_Temp": random.randrange(0, 50),
                    "BT1_FR_Brake_Temp": random.randrange(0, 50),
                    "BT1_RL_Brake_Temp": random.randrange(0, 50),
                    "BT1_RR_Brake_Temp": random.randrange(0, 50),
                    "Hoist_Cyl_Len": random.randrange(0, 50),
                    "Dump_Cyl_Len": random.randrange(0, 50),
                    "Accelerator_Pedal": random.randrange(0, 50),
                    "Battery": random.randrange(0, 50),
                    "Accumulator": random.randrange(0, 50),
                    "Transmission_oil": random.randrange(0, 50),
                    "Brake_Return": random.randrange(0, 50),
                    "Hydraulic_Reflux": random.randrange(0, 50),
                    "Up_Box_Oil": random.randrange(0, 50),
                    "Pilot": random.randrange(0, 50),
                    "Dump_Cyl_Extend": random.randrange(0, 50),
                    "Dump_Cyl_Retract": random.randrange(0, 50),
                    "Hoist_Cyl_Extend": random.randrange(0, 50),
                    "Hoist_Cyl_Retract": random.randrange(0, 50),
                    "Steering_Cyl_LH_Extend": random.randrange(0, 50),
                    "Steering_Cyl_RH_Extend": random.randrange(0, 50),
                    "Service_Brake": random.randrange(0, 50),
                    "Parking_Brake": random.randrange(0, 50),
                    "Diesel": random.randrange(0, 50),
                    "Hydraulic_Oil": random.randrange(0, 50),
                    "Brake_Cooling_Oil": random.randrange(0, 50),
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