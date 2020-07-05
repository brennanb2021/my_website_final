from app.newsScraperDebate.sentimentAnalysis import readArticles
from app.newsScraperDebate.scraper import getArticlesCNN, getArticlesNYT, getArticlesDW, getArticlesFOX, getArticlesHP, getArticlesNYP
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def mainActionDebate(keywords, sources):
    keywords = keywords.lower()
    keywordArr = keywords.split(", ")
    options = Options()
    options.add_argument("--incognito")
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    driver = webdriver.Chrome(str(os.environ.get('CHROMEDRIVER_PATH')), options=options)
    driver.set_page_load_timeout(5)

    rtn = [] #array of data
    
    #analyze all news sources chosen
    for i in sources:
        if ("New York Post articles (50)") == i:
            val = readArticles(getArticlesNYP(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No New York Post articles found"]

        if ("CNN articles (50)") == i:
            val = readArticles(getArticlesCNN(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No CNN articles found"]

        if ("New York Times articles (50)") == i:
            val = readArticles(getArticlesNYT(keywordArr, driver), keywordArr) #NEEDS AN ACCOUNT
            if val != False:
                rtn.append(val)
            else:
                return [False, "No New York Times articles found"]

        if ("Daily Wire articles (50)") == i:
            val = readArticles(getArticlesDW(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Daily Wire articles found"]

        if ("FOX articles (50)") == i:
            val = readArticles(getArticlesFOX(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No FOX articles found"]

        if ("Huffington Post articles (50)") == i:
            val = readArticles(getArticlesHP(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Huffington Post articles found"]

    driver.quit()
    return rtn