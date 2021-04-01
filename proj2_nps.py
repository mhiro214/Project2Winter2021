#################################
##### Name: Hiroyuki Makino #####
##### Uniqname: mhiro       #####
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}


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
        if site_url in CACHE_DICT.keys():
            print("Using cache")
            html_text = CACHE_DICT[site_url]
        else:
            print("Fetching")
            html = requests.get(site_url)
            html_text = html.text
            CACHE_DICT[site_url] = html_text
        soup = BeautifulSoup(html_text, 'html.parser')
        try:
            self.name = soup.find_all('a', class_="Hero-title")[0].get_text().strip()
            if self.name == "":
                self.name = "no name"
        except:
            self.name = "no name"
        try:
            self.category = soup.find_all('span', class_="Hero-designation")[0].get_text().strip()
            if self.category == "":
                self.category = "no category"
        except:
            self.category = "no category"
        try:
            locality = soup.find_all('span', itemprop="addressLocality")[0].get_text().strip()
            if locality == "":
                locality = "no address"
        except:
            locality = "no address"
        try:
            region = soup.find_all('span', itemprop="addressRegion")[0].get_text().strip()
            if region == "":
                region = "no city"
        except:
            region = "no city"

        self.address = locality + ", " + region

        try:
            self.zipcode = soup.find_all('span', itemprop="postalCode")[0].get_text().strip()
            if self.zipcode == "":
                self.zipcode = "no zipcode"
        except:
            self.zipcode = "no zipcode"
        try:
            self.phone = soup.find_all('span', itemprop="telephone")[0].get_text().strip()
            if self.phone == "":
                self.phone = "no phone"
        except:
            self.phone = "no phone"


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
    if state_url in CACHE_DICT.keys():
        print("Using cache")
        html_text = CACHE_DICT[state_url]
    else:
        print("Fetching")
        html = requests.get(state_url)
        html_text = html.text
        CACHE_DICT[state_url] = html_text
    soup = BeautifulSoup(html_text, 'html.parser')
    parklist = soup.find_all('div', id='parkListResultsArea')[0]
    list_h3 = parklist.find_all('h3')
    list_ns = list()
    
    for h3 in list_h3:
        link = h3.find_all('a')[0]
        site_url = link.get('href')
        site_url = 'https://www.nps.gov' + site_url
        list_ns.append(get_site_instance(site_url))
    
    return list_ns


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
    zipcode = site_object.zipcode
    baseurl = 'http://www.mapquestapi.com/search/v2/radius'
    params = {"key": secrets.API_KEY, "origin": zipcode, "radius": 10,
     "maxMatches": 10, "ambiguities": "ignore", "outFormat": "json"}

    if zipcode in CACHE_DICT.keys():
        print("Using cache")
        dict_places = CACHE_DICT[zipcode]
        return dict_places
    else:
        print("Fetching")
        response = requests.get(baseurl, params=params)
        dict_places = json.loads(response.text)
        CACHE_DICT[zipcode] = dict_places
        return dict_places

def print_nearby_places(dict_places):
    '''Print API data from MapQuest API.
    
    Parameters
    ----------
    dict_places: dict
        an dictionary from MapQuest API
    
    Returns
    -------
    None
    '''
    list_places = dict_places['searchResults']
    for place in list_places:
        name = place['name']
        category = place['fields']['group_sic_code_name']
        if category == "":
            category = "no category"
        address = place['fields']['address']
        if address == "":
            address = "no address"
        city = place['fields']['city']
        if city == "":
            city = "no city"
        print(f'- {name} ({category}): {address}, {city}')
    print()


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def valid_num(inp, len_list):
    ''' Check if the input is valid for the Step 3 of Part 5
    
    Parameters
    ----------
    inp: strings
        Input
    len_list: int
        length of the list of national sites
    
    Returns
    -------
    ret: bool
        True: valid input
        False: invalid input
    '''

    try:
        inp = int(inp)
        if (1 <= inp) and (inp <= len_list):
            return True
        else:
            return False

    except:
        return False


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    if 'https://www.nps.gov/index.htm' in CACHE_DICT.keys():
        print("Using cache")
        dict_states = CACHE_DICT['https://www.nps.gov/index.htm']
    else:
        print('Fetching')
        dict_states = build_state_url_dict()
        CACHE_DICT['https://www.nps.gov/index.htm'] = dict_states


    while True:
        state = input("Enter a state name (e.g., Michigan, michigan) or 'exit': ")
        state = state.lower()

        if state == 'exit':
            print('Bye!')
            break
        elif state not in dict_states.keys():
            print('[Error] Enter a proper state name')
        else:
            state_url = dict_states[state]
            list_ns = get_sites_for_state(state_url)
            title = 'List of national sites in ' + state[0].upper() + state[1:]
            print('-' * len(title))
            print(title)
            print('-' * len(title))
            for i in range(len(list_ns)):
                print(f'[{i+1}] ' + list_ns[i].info())
            print('')

            while True:
                num = input("Choose the number for detail search or 'exit' or 'back':")
                if num == 'exit':
                    print('Bye!')
                    break
                elif num == 'back':
                    break
                elif valid_num(num, len(list_ns)):
                    dict_places = get_nearby_places(list_ns[int(num)-1])
                    title = 'Places near ' + list_ns[int(num)-1].name
                    print('-' * len(title))
                    print(title)
                    print('-' * len(title))                    
                    print_nearby_places(dict_places)
                    
                else:
                    print('[Error] Invalid input')
                    print('')
                    print('----------------------')
            if num == 'exit':
                break


         
    # dict_places = get_nearby_places(get_site_instance("https://www.nps.gov/rira/index.htm"))
    # print_nearby_places(dict_places)

    # Save cache
    save_cache(CACHE_DICT)

