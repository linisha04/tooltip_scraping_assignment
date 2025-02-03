from bs4 import BeautifulSoup
import json

import streamlit as st
import random


import requests

import time

from requests.exceptions import RequestException
import logging
import argparse


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]



logging.basicConfig(
    filename="scraper.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)




max_req=5
time_window =10

req_timestamps=[]
def rate_limiting():
    """this function ensures that only max_req are made within time_window 
       and if limit is exceeded then wait before making the next req
    """
    global req_timestamps
    current_time=time.time() 
    
    req_timestamps = [t for t in req_timestamps if current_time-t<time_window]

            
    if len(req_timestamps)>=max_req:
        #calculate time left in window
        wait_time =time_window-(current_time-req_timestamps[0])
        
        if wait_time > 0:
            logging.info(f"Rate limit is reached. Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        
    req_timestamps.append(time.time())

        
        
            
    
    


    
def fetch_html(url, max_retries=2, timeout=10):
    ''' fetch_html is fetching html content from the given url with retries and error handling

    args are :  url , timeout and max_retries (Max number of retries if request fails)

    return : html content of the given url if request successful else none
    '''
    retries=0
    user_agent = random.choice(USER_AGENTS) 
    headers = {"User-Agent": user_agent}

    while retries<max_retries:
        try:
            rate_limiting() 
            response_recevied= requests.get(url, headers=headers, timeout=timeout)
            response_recevied.raise_for_status() 
           
            logging.info(f"Successfully fetched {url} with UserAgent: {user_agent}")
            
            return response_recevied.text
        
        except RequestException as e :
            logging.error(f"error  in fetching Url {url}: {e}")
            retries += 1
            #adding some delay
            wait=2 ** retries+random.uniform(0.5, 1.5)  
            logging.info(f"retrying in {wait} seconds...")
            time.sleep(wait)
    logging.error("max retries reached. Can not fetch the webpage!!")
   
    return None

    
def parse_tooltip(html_content):
    """This function is used to parse the tooltip information from the html content

    args:html_content : html content of the webpage

    returns: list of dictionary containing tag name, tooltip and information
    """

    #loads the html content into beautiful soup
    soup=BeautifulSoup(html_content, 'html.parser')
    tooltip_elements=soup.find_all(lambda tag: tag.has_attr("title"))
    
    extracted_data=[]
    for element in tooltip_elements:
        tooltip_text=element.get("title") 
        tag_name=element.name

        # if tag_name=="img" and (tooltip_text== ""):
        #     continue

        
        # skip if title is empty
        if tooltip_text=="":
            continue

    
        # extract information from the tag
        if element.get_text(strip=True):
            element_text=element.get_text(strip=True)
        else:
            continue

        # append the extracted data to the list
        
        extracted_data.append({
            "tag":tag_name,
            "tooltip":tooltip_text,
            "information":element_text
        })
    return extracted_data

def saving_json(extracted_data):
    filename="tooltips_info.json"

    '''this function is used to save the extracted data to the json file'''
    try:
        with open(filename,"w",encoding="utf-8") as file:
            json.dump(extracted_data,file,  indent=4,ensure_ascii=False)
            logging.info("Data successfully saved in tooltips_info.json")
    except Exception as e:
        logging.error(f"error in saving JSON file: {e}")
        
        


    
def tooltip_scraping_function(url):
    '''this function is used to scrape the tooltip information of the website from the given url

    args: url of the website


    '''

    logging.info(f"Starting tooltip scraping for: {url}")
    start_time = time.time()

    #calling fetch_html functions to get the html content of the website
    html_content=fetch_html(url)
    if html_content:
        # calling parse_tooltip function to get the tooltip information of the website
        data=parse_tooltip(html_content)
        if not data:
            logging.warning("No tooltip data found on the page.")
        else:
            saving_json(data)
            end_time = time.time()
            logging.info(f"Scraping completed in {end_time-start_time:.2f} seconds!!")
    else:
        logging.error("No HTML data received. Now exiting...")
    
    time.sleep(2) 

if __name__ =="__main__":


    parser=argparse.ArgumentParser(description="Web Scraper for Tooltip Extraction")
    parser.add_argument("--url",required=True,help="website URL to scrape")
    args=parser.parse_args()

    tooltip_scraping_function(args.url)

    
    # target_url="https://www.flipkart.com/"

    # target_url="https://www.cbse.gov.in/"
    
    # target_url="https://cga.nic.in/"
  
    # tooltip_scraping_function(target_url)

        
    
    
    