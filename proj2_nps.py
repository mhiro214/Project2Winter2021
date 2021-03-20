#################################
##### Name: Hiroyuki Makino #####
##### Uniqname: mhiro       #####
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, site_url):
        html = requests.get(site_url)
        html_text = html.text
        soup = BeautifulSoup(html_text, 'html.parser')
        self.name = soup.find_all('a', class_="Hero-title")[0].get_text().strip()
        self.category = soup.find_all('span', class_="Hero-designation")[0].get_text().strip()
        locality = soup.find_all('span', itemprop="addressLocality")[0].get_text().strip()
        region = soup.find_all('span', itemprop="addressRegion")[0].get_text().strip()
        self.address = locality + ", " + region
        self.zipcode = soup.find_all('span', itemprop="postalCode")[0].get_text().strip()
        self.phone = soup.find_all('span', itemprop="telephone")[0].get_text().strip()


    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'



def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    dict_states = dict()
    html = requests.get('https://www.nps.gov/index.htm')
    html_text = html.text
    soup = BeautifulSoup(html_text, 'html.parser')
    menu_states = soup.find_all('ul', class_="dropdown-menu SearchBar-keywordSearch")[0]
    list_links = menu_states.find_all('a')
    for link in list_links:
        url = link.get('href')
        url = 'https://www.nps.gov' + url
        name = link.get_text().lower()
        dict_states[name] = url

    return dict_states
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    ns = NationalSite(site_url)
    return ns


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    pass


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

if __name__ == "__main__":
    ns = get_site_instance('https://www.nps.gov/yell/index.htm')
    print(ns.info())