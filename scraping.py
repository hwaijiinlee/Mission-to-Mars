#import splinter and beautifulsoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #initiate headless driver for deployment    
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    
    #set variables
    news_title, news_paragraph = mars_news(browser)

    #run all scraping functions and store results in dictionary
    data = {
            "news_title": news_title,
            "news_paragraph": news_paragraph,
            "featured_image": featured_image(browser),
            "facts": mars_facts(),
            "last_modified": dt.datetime.now()
    }

   #stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    
    #scrape Mars News
    #visit the mars nasa site
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    #optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #convert browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    #add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        #use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()    
        #use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()            
   
    except AttributeError:
       return None, None    

    return news_title, news_p

# ### Featured Images

def featured_image(browser):

    #visit the https://spaceimages-mars.com/ site
    url = 'https://spaceimages-mars.com/'
    browser.visit(url)
    
    #find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    #parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #add try/except for error handling
    try:
        #find relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
            
    except AttributeError:
        return None
    
    #use base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# ## Mars facts
def mars_facts():
    
    try:
        #use read_html to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com/', skiprows=1)[0]
    
    except BaseException:
        return None

    #assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    #convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")        

if __name__=="__main__":
    #if running as script, print scraped data
    print(scrape_all())
