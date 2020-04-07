import datetime
import logging

import azure.functions as func
import requests
from bs4 import BeautifulSoup

def main(mytimer: func.TimerRequest, inputblob: func.InputStream, outputblob: func.Out[func.InputStream]) -> None: #, inputblob: func.InputStream , outputblob: func.Out[func.InputStream]
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    URL = 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/submit-profile/rounds-invitations.html'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    divs = soup.find_all('div', class_='mwsgeneric-base-html parbase section')
    
    invitations_issued = None
    lowest_score = None
    round_date = None

    for div in divs:
        for child in div.contents:
            if child is None or child.name != 'p':
                continue

            if 'Number of invitations issued' in child.text:
                invitations_issued = child.contents[1].strip().replace(',', '')
            
            if 'CRS score of lowest-ranked' in child.text:
                lowest_score = child.contents[1].strip()

            if 'Date and time of round' in child.text:
                round_date_string = child.contents[1].strip()
                cut_index = round_date_string.index(' at')

                round_date = datetime.datetime.strptime(round_date_string[0:cut_index], '%B %d, %Y')

    logging.info(round_date)
    logging.info(invitations_issued)
    logging.info(lowest_score)

    output_string = '{}\n{}\n{}'.format(round_date, invitations_issued, lowest_score)
    logging.info(output_string)

    outputblob.set(output_string)
