from bs4 import BeautifulSoup
import requests
from settings import *

#get website
query = input('Enter query: ').replace('','+')
source = requests.get(f'{url}{query}').text

soup = BeautifulSoup(source, 'lxml')

################ INTRUCTIONAL PURPOSES ##################
"""
###if reading from html file in data
# with open('simple.html') as html_file:
#     soup = BeautifulSoup(html_file, 'lxml')
#print(soup.prettify()) #returns indented HTML

# article = soup.find('div', class_ = 'article')
# summary = article.p.text
# print(summary)

###use for loop to loop through multiple articles
for article in soup.find_all('div',class_='article'):
    summary = article.p.text
    print(summary)
"""
################ INTRUCTIONAL PURPOSES ##################

#print(soup.prettify())



for summary in soup.find_all('div',id = 'main'):


    try:
        a = summary.text

        a=a.replace('·', ' ')
        a= a.replace('›','/')
        a = a.replace('|', '/')


        if 'View allView all' not in a:
            print('ran through try1')
            a = a.split('View all')[1]
            a = space_caps(a).replace('  ',' ')
            if 'Metacritic' in a and 'Rotten Tomatoes' in a:
                a = a.split('Metacritic')[1]
            print(a)

        else:
            print('ran through try2')
            a = a.split('resultsVerbatim')[1].split('View allView all')[0]
            a = space_caps(a).replace('  ', ' ')
            if 'Metacritic' in a and 'Rotten Tomatoes' in a:
                a = a.split('Metacritic')[1]
            print(a)

    except:
        a = summary.text
        a = a.replace('·', ' ')
        a = a.replace('|', '/')
        a = a.replace('›', '/')

        a = a.split('resultsVerbatim')[1]
        a = space_caps(a).replace('  ', ' ')
        print('ran through except')
        if 'Metacritic' in a and 'Rotten Tomatoes' in a:
            a = a.split('Metacritic')[1]
        print(a)



    # except IndexError:
    #     print('ran through except2')
    #     a = summary.text
    #     a = a.replace('·', ' ')
    #     a = a.replace('|', '/')
    #     a = a.replace('›', '/')
    #     a = space_caps(a)
    #     print(a)



    # try:
    #     a = summary.text
    #     a=a.replace('·', ' ')
    #     a=a.replace('›', '/')
    #
    #
    #     print(a.split('resultsVerbatim'))
    # except:
    #     pass