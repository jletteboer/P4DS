import getpass                          # For getting username and password
import requests                         # For getting and posting HTTP requests to URLs
import urllib3                          # For disabling SSL warnings
import os                               # For getting filesize, checking directories an files
from tqdm.notebook import tnrange       # For showing progressbar
import IP2Location                      # IP Geolocation Python Library for getting location
import pandas as pd                     # Import pandas for dataframes and series
import matplotlib.pyplot as plt         # For making plots
import matplotlib.patches as mpatches   # Customizing legends
import seaborn as sns                   # Seaborn visualization package
from scipy import stats                 # For using statistical functions

## Disable warnings about certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Setting colors for printing colored text
GREEN = '\033[1;32;1m'
CEND = '\33[0m'
RED = '\033[1;91;1m'
BOLD = '\033[1m'

## Setting static color 
static_color = '#38a3d8'


def yesNo(question, default_no=True):
    """Ask a yes/no question, give input as answer and return False or True.
    Function will only check first character in answer
    
    Args:
        question   : string  : What is the question you want to be answered with yes or no. 
                               Default is the presumed answer if the user just hits <Enter>. 
        default_no : boolean : True or False

    Returns:
        Returns value is True for "yes" or False for "no".
        
    Example:
        yesNo("Do you want to download the file via Splunk API?")
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


def downloadData(search_user, app, searchname, path, output_file, output_type = 'csv', host = 'localhost'):
    """Download data from Splunk API.

    Args:
        search_user : string : Splunk search owner
        app         : string : Splunk App name where search belongs to
        searchname  : string : Savedsearch name
        path        : string : Path to save file e.q. '../data/' 
        output_file : string : Where to output the events (including path), e.q. data/test.csv
        output_type : string : Which type of file for output (csv, json, raw, xml)
        host        : string : Hostname of Splunk server

    Returns:
        An file with the downloaded events of the search.

    Example:
        downloadData('user1', 'search', 'webserver_logging_search', '../data/', 'webserver_log', 'csv', 'localhost')
    """
    
    ## Ask user if we must downloading the file from API
    if yesNo("Do you want to download new data?"):
        
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
            
            ## Check if path exists
            dir_check = os.path.isdir(path)
            if not dir_check:
                os.makedirs(path)
                print(f'Directory {RED}{path} not exists{CEND}, created directory')
            else:
                print(f'Directory {GREEN}{path} already exists{CEND}.')   
            
            ## Save file to disk
            filename = path + output_file + "." + output_type
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
        
        
def getLocation(ip):
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
            getLocation("172.217.168.195")
    '''
    ## Cache the database into memory to accelerate lookup speed.
    ## WARNING: Please make sure your system have sufficient RAM to use this feature.
    database = IP2Location.IP2Location(os.path.join("..", "data", "IP2LOCATION-LITE-DB5", "IP2LOCATION-LITE-DB5.BIN"))
    
    ## Get all information of IP Address
    result = database.get_all(ip)
    
    ## Define names for panda Series
    names = {'clientip': result.ip,
             'country_short': result.country_short,
             'country_long': result.country_long,
             'region': result.region,
             'city': result.city,
             'latitude': result.latitude,
             'longitude': result.longitude}
    
    locations = pd.Series(data=names)
    
    return locations


def httpStatusClass(series: str):
    '''Convert HTTP status code to HTTP Class
    
    Args:
        series : string : Series data

    Returns:
        Returns the class of a HTTP status code.
        
    Example:
        httpStatusClass(df['http_status'])
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

def dataGroupby(df, by, top=15):
    '''This function returns a topN, counted, groupedby dataframe
    
    Args:
        df  : DataFrame : Dataframe
        by  : string    : Wich column must be grouped and counted
        top : int       : How many values will be returned, topN
        
    Returns:
        Return dataframe with topN of grouped column
        
    Example:
        dataGroupby(dataframe, country)
    '''
    ## Create new dataset based on given inputs, count, sort values and return given top
    data = pd.DataFrame(df.groupby(by).size().sort_values(ascending=False)[:top], columns=['count'])
    
    return data


def countryDropdown(df, Country, Top):
    '''This function wil be used for widget interaction of chosen country and returns two barplots with Country and City
    
    Args:
        df      : DataFrame : Dataframe with country and city colmns
        Country : string    : Country list that will show in the dropdown
        Top     : int       : Number op ow many values wil be returned
    
    Returns:
        Two barplots of Country and city with dropdown for Country choice and slider for topN.
        
    Example:
        ## Setting top for creating country_list as input for interaction
        set_top = 20

        ## reate country_list for input ineraction
        country_list = data_groupby(df=df_web_ts, by='country_short', top=set_top).index.tolist()

        ## Add option "# All" for all Countries
        country_list.append('# All')

        ## Sort list
        country_list.sort()

        ## Adding dropdown of country_list and slicer for setting the topN
        ## For dataframe we used fixed, so no interact (e.q. dropdown, slicer) will be created
        widgets.interact(countryDropdown, df=fixed(df_web_ts[['country_short','city']]), 
                         Country=country_list, Top=widgets.IntSlider(min=1,max=set_top,value=15));
    '''
    
    ## Create figure, legend for selected item, and setting colors
    fig, axs = plt.subplots(ncols=2, figsize=(15,10))
    edge_color = 'black'
    selected_color = 'orange'
    legend_labels = mpatches.Patch(facecolor=selected_color, label='Selected Country', edgecolor=edge_color)
    
    ## Create dataframe with top countries
    data_country = dataGroupby(df=df, by='country_short', top=Top)
    
    if Country == '# All':
        data = dataGroupby(df=df, by='city', top=Top)
        clrs = [static_color for x in data_country['count']]
        sns.barplot(data=data, x='count', y=data.index, color=static_color, edgecolor=edge_color, 
                    ax=axs[0]).set(title=f'Hits by top {Top} cities', xscale='log')

    else:
        data = dataGroupby(df=df[df['country_short'] == Country], by='city', top=Top)
        clrs = [selected_color if (x == data_country.loc[Country][0]) else static_color for x in data_country['count'] ]
        sns.barplot(data=data, x='count', y=data.index, color=static_color, edgecolor=edge_color, 
                    ax=axs[0]).set(title=f'Hits from top {Top} cities of {Country}', xscale='log')
     
    ## Plot always countries
    sns.barplot(data = data_country, x='count', y=data_country.index, 
                palette=clrs, edgecolor=edge_color, ax=axs[1])\
                .set(title=f'Hits from top {Top} countries', xscale='log');
    
    axs[1].legend(handles=[legend_labels]) 
    
    ## Function will return fig automatticly, if I return fig too two figure will be created twice

    
def pltMovingAverage(timeseries, window, measure='mean', madType='mean', plotBounds=False, plotOutlier=False):
    """Function for plotting timeseries dataframe, with lower, upper bounds and outliers
    
    Args:
        timeseries  : dataframe : Dataframe with timeseries and values
        window      : int       : Rolling window size
        measure     : string    : Measures of Central Tendency, mean, median 
        plotBounds  : bool      : Show confidence intervals
        plotOutlier : bool      : Show anomalies
        
    Returns:
        Lineplot with confidence interfals and outliers
    
    Example:
        pltMovingAverage(ts, 7, plotBounds=True, plotOutlier=True)
    """
    valid = {'mean', 'median'}
    if measure not in valid:
        raise ValueError(f'Results: measure must be one of {valid}')
    elif madType not in valid:
        raise ValueError(f'Results: madType must be one of {valid}')
    
    ## Create rolling measure based on input
    if measure == 'mean':
        rolling_measure = timeseries.rolling(window=window).mean()
    elif measure == 'median':
        rolling_measure = timeseries.rolling(window=window).median()
    
    ## Setting figure size
    plt.figure(figsize=(20, 8))
    
    ## Setting title
    plt.title(f'Moving average with a window size of {window}')
    
    ## Plot rolling mean and actual values
    plt.plot(rolling_measure, "g--", label=f'Moving {measure}')
    plt.plot(timeseries[window:], label="Actual values", color=static_color)
    
    ## If plotBounds is True
    if plotBounds:
        ## Check what madType is
        if madType == 'mean':
            ## Mean absolute deviation 
            ts_mad = timeseries.mad().item()
        elif madType == 'median':
            ## Median absolute deviation 
            ts_mad = stats.median_abs_deviation(timeseries)[0]
        
        ## Create lower and upper bounds
        lower_bound = rolling_measure - ts_mad
        upper_bound = rolling_measure + ts_mad
        
        ## Plot lower and upper bounds
        plt.plot(upper_bound, "m:", markersize=1.5, label="Lower bound / Upper bound")
        plt.plot(lower_bound, "m:", markersize=1.5)
        
        ## If plotOutlier is True, plot outliers
        if plotOutlier:
            ## Create new dataframe, based on input
            outliers = pd.DataFrame(index=timeseries.index, columns=timeseries.columns)
            
            ## Create outlier column
            outliers[timeseries < lower_bound] = timeseries[timeseries < lower_bound]
            outliers[timeseries > upper_bound] = timeseries[timeseries > upper_bound] 

            ## Number of total outliers
            n_outliers = outliers.count()[0]
        
            ## Plot outliers
            plt.plot(outliers, "ro", markersize=5)
            plt.title(f'Moving {measure} with a window size of {window}\n Number of outliers is {n_outliers}')
    
    ## Plot legend
    plt.legend()
    
    