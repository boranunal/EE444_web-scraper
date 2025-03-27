import requests
from bs4 import BeautifulSoup as bs 
import json

# host url
base_url = 'https://www.odtuden.com.tr'

# create a global list of the books
shelf_global = []

# keep the number of books in the list
bookNumber = 0

# returns page content
def getHTML(session, url):
  # request the page, disable redirects
  res = session.get(url, allow_redirects=False)
  if(res.status_code == 200):
    # get the content from the respond message
    html = res.content
    return html
  # if response status code is not 200 return 0
  else:
    return 0

# returns list of tuples from an html
def getShelfFromPage(html):
  global bookNumber   # to count the books
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
    bookNumber = bookNumber + 1
    # print all info about the book
    print(f'{bookNumber}.\tBook Title: {title}')
    print(f'\tLink: {link}')
    print(f'\tPrice: {price}')

    # append the tuple into the list
    shelf.append(book)

  return shelf

# function to return the index of the cheapest book
def getCheapest():
  len_shelf = len(shelf_global)
  trans = str.maketrans({',':'.','.':''})   # define replacements to convert price to float '₺1.700,00' -> '1700.00' 
  min = float(shelf_global[0][2][1:].translate(trans))  # translate the price to float, select first item to be minimum
  i = 1
  index = 0
  while(i<len_shelf):
    price_f = float(shelf_global[i][2][1:].translate(trans))
    if(price_f < min):
      min = price_f   # if the price is smaller than the previous minimum, select the new minimum
      index = i
    i = i+1
  return index

# returns UrunId and UrunKartId
def getItemInfo(html):

  soup = bs(html, 'html.parser')

  productDetail = soup.find("script", type="text/javascript",string=lambda t: t and t.find("productDetailModel") != -1)
  productDetail = productDetail.get_text().splitlines()[2]
  productDetail = productDetail.split(";")[0].removeprefix("var productDetailModel = ")
  productDetail = json.loads(productDetail)
  UrunId = productDetail["product"]["id"]
  UrunKartId = productDetail["product"]["urunKartiId"]

  return UrunId, UrunKartId

# function with a well explanatory name
def addItemToCart(UrunId, UrunKartId, session):
  url = 'https://www.odtuden.com.tr/api/cart/AddToCartV3'
  item = {
  "Adet" : 1,
  "AsortiUrunKartId" : 0,
  "BagliUrunId" : 0,
  "FormId" : 0,
  "KampanyaId" : 0,
  "SelectProductGroupPostInfo" : [],
  "UrunId" : UrunId,
  "UrunKartId" : UrunKartId,
  "UrunNot" : ""
  }
  res = session.post(url, json=item)
  print(f'response status code for added item: {res.status_code}')

# returns BasketProductId which is needed to remove an item from cart
def getBasketProductId(session):
  url = 'https://www.odtuden.com.tr/api/cart/GetMemberCart'
  res = session.get(url)
  cart = json.loads(res.content)['cart']
  item_count = int(cart['totalNumberProducts'])
  print(f'Number of items in the cart: {item_count}')
  # if there is an item in the basket returns the first items basketProductId
  if(item_count > 0):
    basketProductId = cart['products'][0]['basketProductId']
    print(f'basketProductId: {basketProductId}')
    return basketProductId
  # if there is no item return 0
  else:
    return 0 

# remove item from cart
def removeFromCart(session, UrunId, basketProductId):
  url = 'https://www.odtuden.com.tr/api/cart/RemoveProduct'
  item = {"VariantId": UrunId,
          "BasketProductId": basketProductId,
          "CampaignId": 0,
          "Quantity": 1,
          "VirtualProduct": False,
          "VirtualProduct2": False
          }
  res = session.post(url, json=item)
  print(f'response status code for removed item: {res.status_code}')

if __name__ == "__main__":
  # start a session to keep cart state
  session = requests.Session()
  page_url = base_url + '/kitaplik?sayfa='
  for i in range(1,200):
    html = getHTML(session, page_url+str(i))
    # getHTML returns 0 if response status code is not 200
    if(html==0):
      break
    # if the response is OK get the list of books from a page 
    # and append it to the global list of books
    else:
      shelf_global = shelf_global + (getShelfFromPage(html))
  # print the info about the cheapest book
  print('CHEAPEST BOOK: ')
  for i in range(3):
    print(shelf_global[getCheapest()][i])

  # extract info about the cheapest book to add to cart
  cheap_url = shelf_global[getCheapest()][1]
  cheap_html = getHTML(session, cheap_url)
  UrunId, UrunKartId = getItemInfo(cheap_html)
  print('UrunId:', UrunId, '\nUrunKartId:', UrunKartId)
  
  # add cheapest book to cart
  addItemToCart(UrunId, UrunKartId, session)

  # remove item from the cart
  basketProductId = getBasketProductId(session)
  if(basketProductId != 0):
    removeFromCart(session, UrunId, basketProductId)
    getBasketProductId(session)
 