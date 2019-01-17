import requests
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml
import pymongo
import time

def store_one_page(databank, product_dic):
    collection = databank.Net_A_Porter
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

def process_one_page(url, databank, browser):
    reload(sys)
    sys.setdefaultencoding("utf-8")

    html = get_url(browser, url, 5)

    # use BeautifulSoup to get the product info
    soup = BeautifulSoup(html, 'lxml')
    remove_part = soup.find("div", {'class': 'show-hide-content style-scope nap-htwi-module'})
    if remove_part:
        remove_part.decompose()
    remove2 = soup.find("div", {'class': 'show-hide-content style-scope nap-ymal-module'})
    if remove2:
        remove2.decompose()

    # get related info
    product_sizes = soup.find("select", {'id': 'select'})
    product_brand = soup.find("span", {'itemprop': 'name'})
    product_detail = soup.find("meta", {'itemprop': 'name'})
    product_id = soup.find("meta", {'itemprop': 'productID'})
    product_price = soup.find("span", {'class': 'full-price style-scope nap-price'})
    product_sale = soup.find("span", {'class': 'sale sale-price style-scope nap-price'})
    product_discount = soup.find("span", {'class': 'discount style-scope nap-price'})
    product_cate = soup.find("meta", {'itemprop': 'category'})
    num_of_sizes = 0
    if product_sizes:
        for s in product_sizes:
            stock = s.get('data-stock')
            if stock:
                if stock != 'Out_of_Stock':
                    num_of_sizes += 1

    # use a dictionary to store the information of one product
    product = {}
    product['ID'] = product_id.get('content')
    product['Category'] = product_cate.get('content')
    product['Name'] = product_brand.string
    product['Detail'] = product_detail.get('content')
    product['Price'] = product_price.string

    if product_discount:
        product['Discount'] = product_discount.string.encode('ascii', 'ignore')
        product['Sale_price'] = product_sale.string
    else:
        product['Discount'] = 'No discount'
        product['Sale_price'] = 'N/A'

    product['Sizes'] = num_of_sizes

    # store the product info into data bank
    store_one_page(databank, product)
    return

if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'images': 2,}}
    options.add_experimental_option('prefs', prefs)

    # change the following address to the address where you store Chrome Webdriver
    main_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver', chrome_options=options)
    sub_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver', chrome_options=options)

    client = pymongo.MongoClient(host='localhost')
    db = client['Test']

    '''brands = 
    for b in brands:
        if b == 'marc-jacobs' or b == 'loewe':
            break
        else:'''
    # US:
    # brand_url = 'https://www.farfetch.com/shopping/women/'+b+'/items.aspx'
    brands = ['1532', '313']
    for b in brands:
        print 'Current at brand: ' + b
        brand_url = 'https://www.net-a-porter.com/us/en/d/Shop/Sale/all?designerfilter='+b+'&pn=1&npp=60&image_view=product&dScroll=0&sortorder=price-desc'
        main_browser.get(brand_url)
        html = main_browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        page_number = soup.find("div", {'class': 'pagination-links'})
        max_page = int(page_number.get('data-lastpage'))

        print 'Number of pages: ' + str(max_page)
        page = 1  # start at page 1

        while page <= max_page:
            print "At page " + str(page)
            if page != 1:
                main_url = 'https://www.net-a-porter.com/us/en/d/Shop/Sale/all?designerfilter='+b+'&pn='+str(page)+'&npp=60&image_view=product&dScroll=0&sortorder=price-desc'
                main_browser.get(main_url)
            html = main_browser.page_source
            soup3 = BeautifulSoup(html, 'lxml')
            products = soup3.find_all("div", {'class': 'product-image'})
            for p in products:
                product_url = 'https://www.net-a-porter.com' + p.a.get('href')

                process_one_page(product_url, db, sub_browser)
            page += 1


    main_browser.close()
    sub_browser.close()