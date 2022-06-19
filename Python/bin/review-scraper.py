import datetime
import socket
from time import sleep
import requests
from bs4 import BeautifulSoup
import pandas as pd

reviewlist = []
print("inizio")
HOST = "10.0.100.37"  # The server's hostname or IP address10.0.100.37
PORT = 1234  # The port used by the server

def get_soup(url):#ritorna la pagina html che contiene le recensioni
    #richiede la pagina dell'url tramite splash, r  è la pagina html che ci interessa
    r = requests.get('http://10.0.100.50:8050/render.html', params={'url': url, 'wait': 2})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_reviews(soup): #fornisce una lista i cui elementi sono dizionari
    reviews = soup.find_all('div', {'data-hook': 'review'}) #restituisce una lista di reviews
    try:
        for item in reviews:
            country = item.find('span', {'data-hook': 'review-date'}).text.strip().split(" ")[-5]
            try:
                verify = item.find('span', {'data-hook': 'avp-badge'}).text.strip()
            except:
                verify = "Not Verified"
            if (country == "Kingdom"):
                review = {
            'product': soup.title.text.replace('Amazon.co.uk:Customer reviews:', '').strip(),
            'title': item.find('a', {'data-hook': 'review-title'}).text.strip(),
            'rating': item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip(),
            'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            'date': item.find('span', {'data-hook': 'review-date'}).text.split("on")[1].strip(),
            'country': "United Kingdom",
            'verified': verify
             }
            else:
                review = {
            'product': soup.title.text.replace('Amazon.co.uk:Customer reviews:', '').strip(),
            'title': item.find('span', {'data-hook': 'review-title'}).text.strip(),
            'rating': item.find('i', {'data-hook': 'cmps-review-star-rating'}).text.replace('out of 5 stars', '').strip(),
            'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            'date': item.find('span', {'data-hook': 'review-date'}).text.split("on")[1].strip(),
            'country': country,
            'verified': verify
            }
            
            if (review != None):
                date_time_obj = datetime.datetime.strptime(review['date'], '%d %B %Y')
                review['date'] = str(date_time_obj.date())
                #print(review['title'])
                r = requests.post('http://10.0.100.37:1234', json=
                {
                    "product":  review['product'],
                    "title":  review['title'],
                    "rating":  review['rating'],
                    "tweet":  review['body'],
                    "date" : review['date'],
                    "country": review['country'],
                    "verified": review['verified']
                })
                reviewlist.append(review)
    except:
        pass

sleep(60)
isin = "B09MRZHJB7"
for x in range(1, 500):
    soup = get_soup(f'https://www.amazon.co.uk/product-reviews/{isin}/ref=cm_cr_arp_d_paging_btm_next_{x}?pageNumber={x}')
    print(f'Getting page: {x}')
    get_reviews(soup)
    l = len(reviewlist)
    print(l)

    if not soup.find('li', {'class': 'a-disabled a-last'}):    
        pass
    else:
        break

# df = pd.DataFrame(reviewlist)
# df.to_excel('sony-headphones.xlsx', index=False)
print('Fin.')
