import requests
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import lxml
import pymongo
import time

def store_one_page(databank, product_dic, gender):
    '''if gender == 'women':
        collection = databank.Fargetch_Women
    else:
        collection = databank.Fargetch_Men'''
    collection = databank.Fargetch_Women
    result = collection.insert_one(product_dic)
    return result

def get_url(browser,url,num_retries):
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

def process_one_page(url, databank, browser, gender):
    reload(sys)
    sys.setdefaultencoding("utf-8")

    # change the page to US market, not needed if the script is run in US
    '''button1 = browser.find_element_by_id('ff-bob-cntrslt') # find the market button
    button1.click()
    time.sleep(1)
    button2 = browser.find_element_by_xpath('//li[@data-test="change_locale_761"]')
    button2.click()'''

    html = get_url(browser, url, 5)

    # use BeautifulSoup to get the product info
    soup = BeautifulSoup(html, 'lxml')
    remove_part = soup.find("div", {'class': '_3d7312'})
    if remove_part:
        remove_part.decompose()

    # get the product store ID
    temp = ''
    id = ''
    for k in range(len(url) - 1, 0, -1):
        if url[k] == '-':
            begin = k
            break
        elif url[k] == '.':
            end = k
    for i in range(begin + 1, end, +1):
        id += url[i]


    # get related info
    product_name = soup.find(attrs={'data-tstid': 'cardInfo-title'})
    if product_name:
        product_name = product_name.string
    else:
        return
    product_detail = soup.find(attrs={'data-tstid': 'cardInfo-description'}).string
    product_price = soup.find(attrs={'data-tstid': 'priceInfo-original'})
    product_discount = soup.find(attrs={'data-tstid': 'priceInfo-discount'})
    product_dealprice = soup.find(attrs={'data-tstid': 'priceInfo-onsale'})
    #time.sleep(1)

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
                    for c in s:  # get rid of '.' in size like from 36.5 to 36_5
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
    store_one_page(databank, product, gender)
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
    # full list:
    # brands = ['marc-jacobs', 'loewe', 'alexander-mcqueen', '15005-designer-mcq-alexander-mcqueen', 'bottega-veneta', 'fendi', 'valentino', 'tom-ford', 'versace', 'miu-miu', 'designer-givenchy', 'balenciaga', 'off-white', 'thom-browne', 'canada-goose', 'kenzo', 'gucci', 'burberry', 'prada', 'saint-laurent', 'dolce-gabbana', 'moncler']
    #genders = ['women', 'men']
    g = 'women'
    #for g in genders:
    '''if g == 'women':
        brands = ['miu-miu', 'designer-givenchy', 'balenciaga', 'off-white',
                  'thom-browne', 'canada-goose', 'kenzo', 'gucci', 'burberry', 'prada', 'saint-laurent',
                  'dolce-gabbana', 'moncler']
    else:
        brands = ['marc-jacobs', 'loewe', 'alexander-mcqueen', '15005-designer-mcq-alexander-mcqueen', 'bottega-veneta', 'fendi', 'valentino', 'tom-ford', 'versace', 'miu-miu', 'designer-givenchy', 'balenciaga', 'off-white', 'thom-browne', 'canada-goose', 'kenzo', 'gucci', 'burberry', 'prada', 'saint-laurent', 'dolce-gabbana', 'moncler']
    '''

    # brands = ['kenzo', 'gucci', 'burberry', 'prada', 'saint-laurent','dolce-gabbana', 'moncler']
    # brands = ['thom-browne', 'canada-goose', 'kenzo', 'gucci', 'burberry', 'prada', 'saint-laurent', 'dolce-gabbana', 'moncler']
    brands = ['salvatore-ferragamo']
    for b in brands:
        '''if b == 'marc-jacobs' or b == 'loewe':
            break
        else:'''
        # US:
        # brand_url = 'https://www.farfetch.com/shopping/women/'+b+'/items.aspx'
        brand_url = 'https://www.farfetch.cn/cn/shopping/'+g+'/'+b+'/items.aspx?page=1&view=180&sort=1&scale=284'
        main_browser.get(brand_url)
        main_browser.execute_script("scrollBy(0,10000);")
        time.sleep(2)
        html = main_browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        pages = soup.find(attrs={'data-test': 'page-number'})
        if pages:
            temp = pages.string
            if temp[-2] == ' ':
                max_page = int(temp[-1])
            else:
                temp2 = temp[-2] + temp[-1]
                max_page = int(temp2)
        else:
            max_page = 1
        page = 1  # start at page 1
        print "Current Brand: " + b
        print "Max pages: " + str(max_page)
        while page <= max_page:
            print "At page" + str(page)

            # change shopping/women to shopping/men can change the gender
            # US:
            # brand_url = 'https://www.farfetch.com/shopping/women/'+b+'/items.aspx?page='+str(page)+'&view=180&sort=1&scale=284'
            if page != 1:
                main_url = 'https://www.farfetch.cn/cn/shopping/' + g + '/' + b + '/items.aspx?page=' + str(
                    page) + '&view=180&sort=1&scale=284'
                main_browser.get(main_url)
                main_browser.execute_script("scrollBy(0,10000);")

            time.sleep(2)
            html = main_browser.page_source
            soup = BeautifulSoup(html, 'lxml')
            products = soup.find_all(attrs={'itemprop': "url"})

            for p in products:
                if p.get('href'):
                    url = 'https://www.farfetch.cn' + p.get('href')
                    process_one_page(url, db, sub_browser, g)

            page += 1

    main_browser.close()
    sub_browser.close()
