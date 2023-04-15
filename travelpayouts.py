import os
import requests

class TravelpayoutsParser:
    PRICES_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin={org_iata}&destination={dst_iata}&currency=rub&departure_at={dep_date}&sorting=price&direct=true&limit=1"
    PLACES_URL = 'https://autocomplete.travelpayouts.com/places2?locale=en&types[]=airport&types[]=city&term='

    def make_price_request(self, org_iata, dst_iata, dep_date, ret_date):
        headers = {'Accept-Encoding': 'gzip, deflate'}
        url = self.PRICES_URL.format(org_iata=org_iata, dst_iata=dst_iata, dep_date=dep_date)
        url = url + "&token=" + os.environ.get('TP_TOKEN')
        if ret_date != "":
            url = url + "&return_at=" + ret_date
        r = requests.get(url, headers=headers)

        return r.json()

    def translate_to_iata(self, text):
        result = requests.get(self.PLACES_URL + text)
        if result.json() == []:
            return ""
        else:
            return result.json()[0]['code']
