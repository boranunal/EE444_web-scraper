import requests
from bs4 import BeautifulSoup as bs 

# host name, entry point
base_url = 'https://www.odtuden.com.tr'
url = base_url + '/kitaplik'

# request the page
res = requests.get(url)

# get the content from the respond message
html = res.content

# parse html
soup = bs(html, 'html.parser')

# find product item tag, this is where individual products are,
# iterate through item_tags to get each item
item_tag = soup.find('div', class_='productItem')

# find anchor tag, this is where title and link is found as attributes
anchor_tag = item_tag.find('a')

# get title
title = anchor_tag.get('title').strip()

# get link
link = url + anchor_tag.get('href').strip()

# find the tag where the price is, 
# get the priceD
price = item_tag.find('span', class_='discountPriceSpan').text.strip()

print('Title: ', title)
print('Link: ', link)
print('Price: ', price)


