import requests
from bs4 import BeautifulSoup as bs 

# host name, entry point
base_url = 'https://www.odtuden.com.tr'

# create a global list
shelf_global = []

def getHTML(url):
    # request the page
  res = requests.get(url, allow_redirects=False)
  if(res.status_code == 200):
    # get the content from the respond message
    html = res.content
    return html
  else:
    return 0

def getShelfFromPage(html):  
  # create a list
  shelf = []

  # parse html
  soup = bs(html, 'html.parser')

  # find each book on the page
  item_tags = soup.find_all('div', class_='productItem')

  for item_tag in item_tags:
    # get anchor tag
    anchor_tag = item_tag.find('a')
    # get book title
    title = anchor_tag.get('title').strip()
    # get book link
    link = base_url + anchor_tag.get('href').strip()
    # get book price
    price = item_tag.find('span', class_='discountPriceSpan').text.strip()
    # construct a tuple
    book = (title, link, price)
    # append the tuple into the list
    shelf.append(book)

  return shelf



if __name__ == "__main__":
  page_url = base_url + '/kitaplik?sayfa='
  for i in range(1,200):
    html = getHTML(page_url+str(i))
    if(html==0):
      break
    else:
      shelf_global = shelf_global + (getShelfFromPage(html))
  
  k = 1
  for i in shelf_global:
    print(str(k)+'.', end='')
    k = k+1
    for j in i:
      print('\t'+ j)
