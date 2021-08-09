#!/usr/bin/env python
# coding: utf-8

# In[13]:


import requests
from glob import glob
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import sleep

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


def search_product_list(interval_count = 1, interval_hours = 6):
    
    prod_tracker = pd.read_csv('trackers/TRACKER_PRODUCTS.csv', sep=';')
    prod_tracker_URLS = prod_tracker.url
    tracker_log = pd.DataFrame()
    now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')
    interval = 0 #counter initialization


    while interval < interval_count:

        for x, url in enumerate(prod_tracker_URLS):
            page = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(page.content, features="lxml")
            
            #product title
            title = soup.find(id='productTitle').get_text().strip()
            
            # to prevent script from crashing when there isn't a price for the product
            try:
                price = soup.find(id ='priceblock_ourprice').get_text().replace('₹','')
            except:
                # this part gets the price in dollars from amazon.com store
                try:
                    price = soup.find(id ='priceblock_ourprice').get_text().replace('₹','')
                except:
                    price = ''

            try:
                review_score = soup.select('.a-star-4-5')[0].get_text()
                review_count = soup.select('#acrCustomerReviewText')[0].get_text()
            except:
                # sometimes review_score is in a different position... had to add this alternative with another try statement
                try:
                    review_score = float(soup.select('i[class*="a-icon a-icon-star a-star-"]')[1].get_text().split(' ')[0].replace(",", "."))
                    review_count = soup.select('#acrCustomerReviewText')[0].get_text()
                except:
                    review_score = ''
                    review_count = ''
            
            # checking if there is "Out of stock"
            try:
                soup.select('#availability .a-color-state')[0].get_text().strip()
                stock = 'Out of Stock'
            except:
                # checking if there is "Out of stock" on a second possible position
                try:
                    soup.select('#availability .a-color-state')[0].get_text().strip()
                    stock = 'Out of Stock'
                except:
                    # if there is any error in the previous try statements, it means the product is available
                    stock = 'Available'

            log = pd.DataFrame({'date': now.replace('h',':').replace('m',''),
                                'code': prod_tracker.code[x], # this code comes from the TRACKER_PRODUCTS file
                                'url': url,
                                'title': title,
                                'buy_below': prod_tracker.buy_below[x], # this price comes from the TRACKER_PRODUCTS file
                                'price': price,
                                'stock': stock,
                                'review_score': review_score,
                                'review_count': review_count}, index=[x])

            try:
                # This is where you can integrate an email alert!
                if price < prod_tracker.buy_below[x]:
                    print('************************ ALERT! Buy the '+prod_tracker.code[x]+' ************************')
            
            except:
                # sometimes we don't get any price, so there will be an error in the if condition above
                pass

            tracker_log = tracker_log.append(log)
            print('appended '+ prod_tracker.code[x] +'\n' + title + '\n\n')            
            sleep(5)
        
        interval += 1# counter update
        
        sleep(interval_hours*1*1)
        print('end of interval '+ str(interval))
    
    # after the run, checks last search history record, and appends this run results to it, saving a new file
    last_search = glob('C:/Users/shiva/Search_History*.xlsx')[-1] # path to file in the folder
    search_hist = pd.read_excel(last_search)
    final_df = search_hist.append(tracker_log, sort=False)
    
    final_df.to_excel('Search_History/SEARCH_HISTORY_{}.xlsx'.format(now), index=False)
    print('end of search')

search_product_list()

