import requests
import json
import pyttsx3
import speech_recognition as sr
import re

API_KEY = "t5-nDuna8ATJ"
Project_Token = "tm__p-2tC9o4"
Run_Token = "tDVd52A_Ar9J"


class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',
                                params=self.params)
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        total = self.data['total']
        for content in total:
            if content['name'] == 'Coronavirus Cases:':
                return content["value"]
            else:
                return "0"

    def get_total_deaths(self):
        total = self.data['total']
        for content in total:
            if content['name'] == "Deaths:":
                return content['value']
        else:
            return "0"

    def get_country_data(self, country):
        countries = self.data['country']
        for item in countries:
            if item['name'].upper() == country.upper():
                return item
        else:
            return "0"

    def get_country_list(self):
        list_country = []
        countries = self.data['country']
        for country in countries:
            list_country.append(country['name'].lower())
        return list_country


# d = Data(api_key=API_KEY, project_token=Project_Token)
# print(d.data)
# print(d.get_country_list())
# print(d.get_total_deaths())
# print(d.get_country_data('Tunisia'))


def speak(text):
    engine = pyttsx3.init()
    en_voice_id = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
    # Use female English voice
    engine.setProperty('voice', en_voice_id)
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception", str(e))

    return said.lower()


# print(get_audio())
def main():
    print("Started Program")
    data = Data(api_key=API_KEY, project_token=Project_Token)
    end_phrase = "stop"
    country_list = data.get_country_list()

    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ case"): data.get_total_cases,
        re.compile("[\w\s]+ total case"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths
    }
    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
    }
    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                # print("Okayyyyy")
                result = func()
                break
        if result:
            speak(result)

        if end_phrase in text:  # stop loop
            print("Exit")
            break


main()

