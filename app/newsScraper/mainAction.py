from app.newsScraper.sentimentAnalysis import readArticles, readHeadlines
from app.newsScraper.scraper import getArticlesCNN, getHeadlinesCNN, getHeadlinesNYT, getArticlesNYT, getHeadlinesWP, getHeadlinesDW, getArticlesDW, getArticlesFOX, getHeadlinesFOX, getHeadlinesHP, getArticlesHP, getHeadlinesNYP, getArticlesNYP
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def mainAction(keywords, sources):
    keywords = keywords.lower()
    keywordArr = keywords.split(", ")
    options = Options()
    
    options.add_argument("--incognito")
    driver = webdriver.Chrome('.\drivers\chromedriver.exe', options=options)
    driver.set_page_load_timeout(5)

    rtn = [] #array of data
    
    #analyze all news sources chosen
    for i in sources:
        if ("CNN headlines (500)") == i:
            val = readHeadlines(getHeadlinesCNN(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No CNN headlines found"]

        if ("New York Post headlines (500)") == i:
            val = readHeadlines(getHeadlinesNYP(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No New York Post headlines found"]
        
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

        if ("New York Times headlines (500-limited)") == i:
            val = readHeadlines(getHeadlinesNYT(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No New York Times headlines found"]

        if ("New York Times articles (50)") == i:
            val = readArticles(getArticlesNYT(keywordArr, driver), keywordArr) #NEEDS AN ACCOUNT
            if val != False:
                rtn.append(val)
            else:
                return [False, "No New York Times articles found"]

        if ("Washington Post headlines (500)") == i:
            val = readHeadlines(getHeadlinesWP(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Washington Post headlines found"]

        if ("Daily Wire headlines (500-limited)") == i:
            val = readHeadlines(getHeadlinesDW(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Daily Wire headlines found"]

        if ("Daily Wire articles (50)") == i:
            val = readArticles(getArticlesDW(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Daily Wire articles found"]

        if ("FOX headlines (500-limited)") == i:
            val = readHeadlines(getHeadlinesFOX(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No FOX headlines found"]

        if ("FOX articles (50)") == i:
            val = readArticles(getArticlesFOX(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No FOX articles found"]

        if ("Huffington Post headlines (500-limited)") == i:
            val = readHeadlines(getHeadlinesHP(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Huffington Post headlines found"]

        if ("Huffington Post articles (50)") == i:
            val = readArticles(getArticlesHP(keywordArr, driver), keywordArr)
            if val != False:
                rtn.append(val)
            else:
                return [False, "No Huffington Post articles found"]

    driver.quit()
    return rtn