import requests
from bs4 import BeautifulSoup as bs 
import json

# host name, entry point
base_url = 'https://www.odtuden.com.tr'

# create a global list
shelf_global = []

bookNumber = 0

def getHTML(session, url):
    # request the page
  res = session.get(url, allow_redirects=False)
  if(res.status_code == 200):
    # get the content from the respond message
    html = res.content
    return html
  else:
    return 0

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

def getItemInfo(html):

  soup = bs(html, 'html.parser')

  productDetail = soup.find("script", type="text/javascript",string=lambda t: t.find("productDetailModel") != -1)
  productDetail = productDetail.get_text().splitlines()[2]
  productDetail = productDetail.split(";")[0].removeprefix("var productDetailModel = ")
  productDetail = json.loads(productDetail)
  UrunId = productDetail["product"]["id"]
  UrunKartId = productDetail["product"]["urunKartiId"]

  return UrunId, UrunKartId

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

def getCart(session):
  url = 'https://www.odtuden.com.tr/api/cart/GetMemberCart'
  res = session.get(url)
  cart = json.loads(res.content)['cart']
  item_count = int(cart['totalNumberProducts'])
  print(f'Number of items in the cart: {item_count}')
  if(item_count > 0):
    basketProductId = cart['products'][0]['basketProductId']
    print(f'basketProductId: {basketProductId}')
    return basketProductId
  else:
    return 0 
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
  session = requests.Session()
  page_url = base_url + '/kitaplik?sayfa='
  for i in range(1,2):
    html = getHTML(session, page_url+str(i))
    if(html==0):
      break
    else:
      shelf_global = shelf_global + (getShelfFromPage(html))

  print('CHEAPEST BOOK: ')
  for i in range(3):
    print(shelf_global[getCheapest()][i])

  cheap_url = shelf_global[getCheapest()][1]
  cheap_html = getHTML(session, cheap_url)
  UrunId, UrunKartId = getItemInfo(cheap_html)
  print('UrunId:', UrunId, '\nUrunKartId:', UrunKartId)
  addItemToCart(UrunId, UrunKartId, session)
  basketProductId = getCart(session)
  if(basketProductId != 0):
    removeFromCart(session, UrunId, basketProductId)
    getCart(session)
 