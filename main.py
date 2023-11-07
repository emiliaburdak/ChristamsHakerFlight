import requests
from data import Flight, Session
import time
import os
import logging
import subprocess

TOKEN = os.environ.get('TELEGRAM_TOKEN')
session = Session()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
check_interval = 60 * 60


def fetch_flight(departure, destinations, date_start, date_end):
    url = f"https://biletyczarterowe.r.pl/api/destynacja/wyszukaj-wylot?iataSkad%5B%5D={departure}&iataDokad%5B%5D={destinations}&dataUrodzenia%5B%5D=1989-10-30&dataMin={date_start}&dataMax={date_end}&oneWay=true"

    while True:
        try:
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:

                flights_amount = len(data)

                for flight in range(flights_amount):
                    data_flight = data[flight]["Data"]
                    price = data[flight]["Cena"]
                    destination = data[flight]["Bilety"][0]["Przylot"]["Iata"]

                    existing_flight = session.query(Flight).filter_by(data_flight=data_flight, destination=destination,
                                                                      price=price).first()
                    if not existing_flight:
                        flight_check = Flight(data_flight=data_flight, destination=destination, price=price)
                        session.add(flight_check)
                        session.commit()

                        send_notification(price, data_flight)

            else:
                logging.error(f"Error fetching data with status code: {response.status_code}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

        time.sleep(check_interval)


def send_message(msg):
    chat_id = get_telegram_chat_id()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"

    response = requests.get(url)
    response_data = response.json()

    if response.status_code == 200 and response_data.get('ok'):
        logging.info(f"Message sent successfully: {msg}")
    else:
        logging.error(f"Failed to send message. Error: {response_data.get('description')}")


def get_telegram_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        data = requests.get(url).json()
        if data["result"]:
            chat_id = data["result"][0]["message"]["from"]["id"]
            return chat_id

        else:
            logging.error("No updates received from Telegram.")
            return None

    except Exception as e:
        logging.error(f"An error occurred while fetching the chat ID: {e}")
        return None


def display_alert(message, tittle):
    apple_script_command = f'display notification "{message}" with title "{tittle}"'
    subprocess.run(["osascript", "-e", apple_script_command])


def send_notification(price, data_flight):
    msg_occasion_price = f"Yuuuupi! The price dropped to {price} to {data_flight}!"
    msg_basic_price = f"{price}, {data_flight}"
    tittle_occasion_price = "The ticket price has dropped!"
    tittle_basic_price = "Ticket price"

    if not price < 1500:
        display_alert(msg_basic_price, tittle_basic_price)
        send_message(msg_basic_price)
    else:
        display_alert(msg_occasion_price, tittle_occasion_price)
        send_message(msg_occasion_price)


if __name__ == "__main__":
    logging.info(fetch_flight("PQC", "KTW,WAW", "2023-11-06", "2023-12-30"))
