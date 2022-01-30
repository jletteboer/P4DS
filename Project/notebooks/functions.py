import subprocess                       # For spawning new processes
import getpass                          # For getting username and password
import requests                         # For getting and posting HTTP/1.1 requests to URLs
import urllib3                          # For disabling SSL warnings
import os                               # For getting filesize
from tqdm.notebook import tnrange       # For showing progressbar
import IP2Location                      # IP Geolocation Python Library for getting location
import pandas as pd                     # Import pandas for dataframes and series

## Disable warnings about certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Setting colors for printing colored text
GREEN = '\033[1;32;1m'
CEND = '\33[0m'
RED = '\033[1;91;1m'
BOLD = '\033[1m'

def yes_or_no(question, default_no=True):
    """Ask a yes/no question via input() and return False or True.
    
    Args:
        question   : string  : What is the question you want to be answered with yes or no. 
                               Default is the presumed answer if the user just hits <Enter>. 
        default_no : boolean : True or False

    Returns:
        Returns value is True for "yes" or False for "no".
        
    Example:
        yes_or_no("Do you want to download the file via Splunk API?")
    """
    
    ## Define choises and defaut answers
    choices = ' [y/N]: ' if default_no else ' [Y/n]: '
    default_answer = 'n' if default_no else 'y'
    
    ## Strip input and turn it to lowercase, minimum if, else checks
    answer = str(input(question + choices)).lower().strip() or default_answer
    
    ## Check the first char in the answer and return True/False
    if answer[0] == 'y':
        return True
    if answer[0] == 'n':
        return False
    else:
        return False if default_no else True


def download_data(search_user, app, searchname, output_file, output_type = 'csv', host = 'localhost'):
    """Download data from Splunk API.

    Args:
        search_user : string : Splunk search owner
        app         : string : Splunk App name where search belongs to
        searchname  : string : Savedsearch name
        output_file : string : Where to output the events (including path), e.q. data/test.csv
        output_type : string : Which type of file for output (csv, json, raw, xml)
        host        : string : Hostname of Splunk server

    Returns:
        An file with the downloaded events of the search.

    Example:
        download_data('user1', 'search', 'webserver_logging_search', 'webserver_log', 'csv', 'localhost')
    """
    
    ## Ask user if we must downloading the file from API
    if yes_or_no("Do you want to download new data?"):
        
        ## Ask for login credentials for Splunk
        print(f'Enter Splunk credentials for downloading new data')
        username = input("Splunk Username:")
        password = getpass.getpass("Splunk Password:")

        ## Setting parameters for POST request
        params = (
            ('output_mode', output_type),
        )

        ## Setting data for POST request
        data = {
            'search': 'loadjob savedsearch=' + search_user + ":" + app + ":" + searchname
        }

        ## Get the data and write it to a local file if connection is OK
        try:
            ## Print status to user
            print(f'Trying to connect ....')
            
            ## Define/construct POST url
            response = requests.post('https://' + host + ':8089/servicesNS/' + search_user + "/" + app + '/search/jobs/export', 
                                     params=params, data=data, verify=False, auth=(username, password))
            ## Check if an error has occurred
            response.raise_for_status()
            
            ## Printing some output for status
            print(f'HTTP Status is {GREEN}OK{CEND}')
            print(f'Trying to download data from {host} via API')
            
            ## Save file to disk
            filename = output_file + "." + output_type
            with open(filename, "w") as f:
                f.write(response.text)
                  
            ## Progressbar based on filesize
            for i in tnrange(os.path.getsize(filename), desc='Complete'):
                pass
            
            ## Print that the download is done
            print(f'Saving file {GREEN}{output_file}.{output_type}{CEND} is {GREEN}done{CEND}')
            print(f'{GREEN}Happy analyzing!! (ツ){CEND}')
        
        ## Error handling
        except requests.exceptions.HTTPError as error_http:
            print(f'{RED}HTTP Error: {error_http}{CEND}')
        except requests.exceptions.ConnectionError as error_connection:
            print(f'{RED}Error Connecting: {error_connection}{CEND}')
        except requests.exceptions.Timeout as error_timeout:
            print(f'{RED}Timeout Error: {error_timeout}{CEND}')
        except requests.exceptions.RequestException as error:
            print(f'{RED}OOps: Something Else: {error}{CEND}')
            
    else:
        print(f'{RED}New data will not be downloaded (︶︿︶){CEND}')
        
        
def get_location(ip):
    '''Get GEO location of given IP address
    
    Args:
        ip : string: An IP address
    
    Returns:
        Pandas Dataframe with the following columns:
            ip            : IP address
            country_short : ISO3166-1 country code (2-digits) of the IP address.
            country_long  : ISO3166-1 country name of the IP address.
            region        : ISO3166-2 region name of the IP address. 
            city          : City name of the IP address.
            latitude      : City latitude of the IP address.
            longitude     : City longtitude of the IP address.
    
    Example:
            get_location("172.217.168.195")
    '''
    ## Cache the database into memory to accelerate lookup speed.
    ## WARNING: Please make sure your system have sufficient RAM to use this feature.
    database = IP2Location.IP2Location(os.path.join("..", "data", "IP2LOCATION-LITE-DB5", "IP2LOCATION-LITE-DB5.BIN"))
    result = database.get_all(ip)
    ## Get all information of IP Address
    
    names = {'clientip': result.ip,
             'country_short': result.country_short,
             'country_long': result.country_long,
             'region': result.region,
             'city': result.city,
             'latitude': result.latitude,
             'longitude': result.longitude}
    
    locations = pd.Series(data=names)
    return locations


def http_status_class(series: str):
    '''Convert HTTP status code to HTTP Class
    
    Args:
        series : string : 

    Returns:
        Returns the class of a HTTP status code.
        
    Example:
        http_status_class(df['http_status'])
    '''
    if series.startswith('1'):
        return "Informational"
    if series.startswith('2'):
        return "Success"
    if series.startswith('3'):
        return "Redirection"
    if series.startswith('4'):
        return "Client errors"
    if series.startswith('5'):
        return "Server errors"

