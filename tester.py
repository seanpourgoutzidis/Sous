import urllib.robotparser
from urllib.parse import urlparse

import requests
import bs4


rp = urllib.robotparser.RobotFileParser()
url = "https://tasty.co/recipe/spicy-rice-noodles-with-ground-pork-and-scallions"

rp.can_fetch("*", url)

res = requests.get(url)
soup = bs4.BeautifulSoup(res.text,"lxml")

# print(soup)

#Select our ingredients from the HTML - should be an UL
# ingredients = soup.select('ul')
# instructions = soup.select('ol')

ingredientsDos = soup.select('ul li')
instructionsDos = soup.select('ol li')

# print(ingredients)
# print(instructions)

# print(ingredientsDos)s

for item in ingredientsDos:
	print(item.text)

print("\n\n")

for item in instructionsDos:
	print(item.text)
# print(instructionsDos)