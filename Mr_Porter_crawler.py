import requests
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import lxml
import pymongo
import time

def get_clear_browsing_button(driver):
    """Find the "CLEAR BROWSING BUTTON" on the Chrome settings page."""
    return driver.find_element_by_css_selector('* /deep/ #clearBrowsingDataConfirm')


def clear_cache(driver, timeout=60):
    """Clear the cookies and cache for the ChromeDriver instance."""
    # navigate to the settings page
    driver.get('chrome://settings/clearBrowserData')

    # wait for the button to appear
    wait = WebDriverWait(driver, timeout)
    wait.until(get_clear_browsing_button)

    # click the button to clear the cache
    get_clear_browsing_button(driver).click()

    # wait for the button to be gone before returning
    wait.until_not(get_clear_browsing_button)

def store_one_page(databank, product_dic):
    collection = databank.Mr_Porter_US
    result = collection.insert_one(product_dic)
    return

def get_url(browser, url, num_retries):
    try:
        browser.get(url)
        html = browser.page_source
        return html
    except Exception as e:
        if num_retries > 0:
            time.sleep(2)
            print(url)
            print('Requests fail, retry!')
            return get_url(browser=browser, url=url, num_retries=num_retries-1)
        else:
            print("Error:%s"%e)
            return

def process_one_page(url, databank):
    reload(sys)
    sys.setdefaultencoding("utf-8")

    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'images': 2, }}
    options.add_experimental_option('prefs', prefs)
    sub_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver', chrome_options=options)
    html = get_url(sub_browser, url, 5)

    # use BeautifulSoup to get the product info
    soup = BeautifulSoup(html, 'lxml')
    remove_part = soup.find("section", {'class': 'product-recommendations'})
    if remove_part:
        remove_part.decompose()

    # get related info
    product_sizes = soup.find("select", {'data-reactid': '.0.0.3.1.3.2.0.1'})
    product_brand = soup.find("span", {'data-reactid': '.0.0.1.1.0.0.0'})
    product_detail = soup.find("span", {'data-reactid': '.0.0.1.1.1.0'})
    product_id = soup.find("input", {'name': 'productId'})
    product_price = soup.find("span", {'class': 'product-details__price--value price-sale'})
    product_cate = soup.find("p", {'class': 'category'})
    num_of_sizes = 0
    if product_sizes:
        for s in product_sizes:
            stock = s.get('data-stock')
            if stock:
                if stock != 'Out_of_Stock':
                    num_of_sizes += 1

    # use a dictionary to store the information of one product
    product = {}
    if product_id:
        product['ID'] = product_id.get('value')
    else:
        print 'Url load failed!'
        sub_browser.close()
        return
    product['Category'] = product_cate.string
    product['Name'] = product_brand.string
    product['Detail'] = product_detail.string
    product['Price'] = product_price.string

    product['Discount'] = 'No discount'
    product['Sale_price'] = 'N/A'

    product['Sizes'] = num_of_sizes

    # store the product info into data bank
    store_one_page(databank, product)
    sub_browser.close()
    return

if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'images': 2,}}
    options.add_experimental_option('prefs', prefs)
    #options.add_argument("--incognito")

    # change the following address to the address where you store Chrome Webdriver

    #sub_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver', chrome_options=options)

    client = pymongo.MongoClient(host='localhost')
    db = client['Test']

    # brands = ['gucci', 'burberry', 'prada', 'saint_laurent', 'moncler', 'moncler_genius',
     #'moncler_grenoble', 'bottega_veneta', 'fendi', 'valentino', 'tom_ford', 'versace', 'givenchy', 'balenciaga',
     #'off_white', 'thom_browne', 'canada_goose', 'loewe', 'mcq_alexander_mcqueen']
    brands = ['dolce_and_gabbana']
    for b in brands:
        print 'Current at brand: ' + b
        main_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver',
                                        chrome_options=options)
        brand_url = 'https://www.mrporter.com/en-us/mens/designers/'+b+'?image_view=product&sortBy=price-desc&pn=1&image_view=product'
        main_browser.get(brand_url)
        html = main_browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        page_number = soup.find("span", {'class': 'page-on'})
        if page_number:
            temp = page_number.string
            max_page = int(temp[-1])
        else:
            max_page = 1

        print 'Number of pages: ' + str(max_page)
        page = 1  # start at page 1
        while page <= max_page:
            print "At page " + str(page)
            if page != 1:
                main_url = 'https://www.mrporter.com/en-us/mens/designers/'+b+'?image_view=product&sortBy=price-desc&pn='+str(page)+'&image_view=product'
                main_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver',
                                                chrome_options=options)
                main_browser.get(main_url)
            html = main_browser.page_source
            soup3 = BeautifulSoup(html, 'lxml')
            products = soup3.find_all("div", {'class': 'product-image tall-product-image'})
            for p in products:
                product_url = 'https://www.mrporter.com' + p.a.get('href')

                process_one_page(product_url, db)
            page += 1
            main_browser.close()

    # main_browser.close()
    # sub_browser.close()
