import requests
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml
import pymongo
import time

def store_one_page(databank, product_dic):
    collection = databank.Fargetch_Women
    result = collection.insert_one(product_dic)
    return result

def process_one_page(url, databank, browser):
    reload(sys)
    sys.setdefaultencoding("utf-8")

    browser.get(url)

    # change the page to US market, not needed if the script is run in US
    '''button1 = browser.find_element_by_id('ff-bob-cntrslt') # find the market button
    button1.click()
    time.sleep(1)
    button2 = browser.find_element_by_xpath('//li[@data-test="change_locale_761"]')
    button2.click()'''

    html = browser.page_source

    # use BeautifulSoup to get the product info
    soup = BeautifulSoup(html, 'lxml')
    remove_part = soup.find("div", {'class': '_3d7312'})
    if remove_part:
        remove_part.decompose()

    # get the product store ID
    temp = ''
    id = ''
    for k in reversed(url):
        if k == '=':
            break
        else:
            temp += k
    for d in reversed(temp):
        id += d

    product_name = soup.find(attrs={'data-tstid': 'cardInfo-title'}).string
    product_detail = soup.find(attrs={'data-tstid': 'cardInfo-description'}).string
    product_price = soup.find(attrs={'data-tstid': 'priceInfo-original'})
    product_discount = soup.find(attrs={'data-tstid': 'priceInfo-discount'})
    product_dealprice = soup.find(attrs={'data-tstid': 'priceInfo-onsale'})
    time.sleep(1)

    # use a dictionary to store the information of one product
    product = {}
    product['ID'] = id
    product['Name'] = product_name.encode('ascii', 'ignore')
    product['Detail'] = product_detail
    if product_price:
        product['Price'] = product_price.string.encode('ascii', 'ignore')
    else:
        product['Price'] = 'Sold Out'
        product['Sizes'] = 'Sold Out'
        return

    if product_discount:
        product['Discount'] = product_discount.string.encode('ascii', 'ignore')
        product['Sale_price'] = product_dealprice.string.encode('ascii', 'ignore')
    else:
        product['Discount'] = 'No discount'
        product['Sale_price'] = 'N/A'

    product['Sizes'] = {}
    product_sizes = soup.find_all(class_='_99335b')

    if product_sizes:
        for size in product_sizes:
            if size is not None:
                s = size.find(attrs={'data-tstid': 'sizeDescription'})
                if s:
                    s = s.text
                    s = s.encode('ascii', 'ignore')
                    for c in s:
                        if c == '.':
                            s = s.replace('.', '_')
                            break
                    scale = size.find(attrs={'data-tstid': 'sizeScale'}).text
                    scale = scale.encode('ascii', 'ignore')
                    last = size.find(attrs={'data-tstid': 'lastOneLeftLabel'}).text
                    if scale:
                        product['Sizes'][s] = [scale]
                    else:
                        product['Sizes'][s] = ['Free Size']

                    if last:
                        product['Sizes'][s].append('Last One')

                    size_price = size.find(attrs={'data-tstid': 'sizePrice'})
                    if size_price:
                        size_p = size_price.text.encode('ascii', 'ignore')
                        product['Sizes'][s].append('Partner Price: ' + size_p)

    # store the product info into data bank
    store_one_page(databank, product)
    return

if __name__ == '__main__':
    main_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver')
    sub_browser = webdriver.Chrome('/Users/fangyuxuansong/Documents/SKU_Crawler/chromedriver')

    client = pymongo.MongoClient(host='localhost')
    db = client['Test']

    page = 1  # start at page 1
    max_page = 4  # the maximum pages the brand have

    while page <= max_page:
        print "Current at "+ str(page)

        main_url = 'https://www.farfetch.cn/cn/shopping/men/off-white/items.aspx?page='+str(page)+'&view=90&sort=1&scale=282'
        main_browser.get(main_url)
        main_browser.execute_script("scrollBy(0,10000);")
        time.sleep(2)
        html = main_browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        products = soup.find_all(attrs={'itemprop': "url"})

        for p in products:
            if p.get('href'):
                url = 'https://www.farfetch.cn' + p.get('href')
                process_one_page(url, db, sub_browser)

        page += 1

    main_browser.close()
    sub_browser.close()
