import time
from app.newsScraper.urlSearch import buildURLCNN, buildURLNYT, buildURLWP, buildURLDW, buildURLFOX, buildURLHP, buildURLNYP
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from fake_useragent import UserAgent

"""
for all getArticles (except for CNN):
1. go through headlines / go through links to articles
2. for each headline get the link to the article and open in new tab
3. parse all sentences in the article
4. close tab, back to main window
5. stop at 50 articles

for all getHeadlines:
1. go through headlines
2. parse headline
3. stop at 500 articles
"""

def getArticlesCNN(keywordArr, driver):
    pageContentArr = []
    breakBadLoad = False
    totalHeadlinesSeen = 0
    pageNum = 1
    while len(pageContentArr) < 50: #read 50 articles total
        URLPage = buildURLCNN(keywordArr, pageNum)
        try:
            driver.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException): #try again
                print("Making new driver")
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
        for j in range(2): #try 2 times
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "cnn-search__result-contents")))
                break
            except TimeoutException:
                driver.get(URLPage)
                time.sleep(2)
                print("Couldn't load page or no more results")
        
        if not breakBadLoad:
            articleBody = driver.find_elements_by_class_name("cnn-search__result-body")
            for article in articleBody:
                pageContentArr.append(article.text.lower())
                totalHeadlinesSeen+=1
                if len(pageContentArr) == 50:
                    break
        pageNum+=1
        breakBadLoad = False

    return pageContentArr

def getHeadlinesCNN(keywordArr, driver):
    rtnHeadlineList = []
    totalHeadlinesSeen = 0
    pageNum = 1
    breakB = False
    breakBadLoad = False
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        URLPage = buildURLCNN(keywordArr, pageNum)
        try:
            driver.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException):
                print("Making new driver")
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
        for j in range(2): #try 2 times
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "cnn-search__result-contents")))
                break
            except TimeoutException:
                print("Couldn't load page or no more results")
                driver.get(URLPage)
                time.sleep(2)
                breakBadLoad = True
        
        if not breakBadLoad:
                
            articleHeadlines = driver.find_elements_by_class_name("cnn-search__result-headline")
            
            for headline in articleHeadlines: #go through all headlines
                text = headline.text.lower()
                totalHeadlinesSeen+=1
                for keyword in keywordArr:
                    if keyword in text: #only save the text if the keyword is in the headline
                        rtnHeadlineList.append(text)
                        if len(rtnHeadlineList) == 500: 
                            breakB = True
                            break
                        break
                if breakB:
                    break
        
        pageNum += 1
        breakBadLoad = False

    return rtnHeadlineList

def getHeadlinesNYT(keywordArr, driver): #maybe load all and then look through articles?
    rtnHeadlineList = []
    URLPage = buildURLNYT(keywordArr)
    driver.get(URLPage)
    driver.implicitly_wait(3)
    totalHeadlinesSeen = 0 #count of all headlines
    past3LoopsHeadlineNumber = []
    breakB = False
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        
        driver.implicitly_wait(3)
        time.sleep(1)

        articleHeadlines = driver.find_elements_by_tag_name("h4")
        past3LoopsHeadlineNumber.append(totalHeadlinesSeen)
        if len(past3LoopsHeadlineNumber) == 4:
            past3LoopsHeadlineNumber.pop(0)
            if past3LoopsHeadlineNumber[0] == past3LoopsHeadlineNumber[1] and past3LoopsHeadlineNumber[1] == past3LoopsHeadlineNumber[2]:
                #no more headlines are being loaded
                break

        for headlineIndex in range(totalHeadlinesSeen, len(articleHeadlines)-1): #go through all headlines
            text = articleHeadlines[headlineIndex].text.lower()
            totalHeadlinesSeen+=1
            for keyword in keywordArr:
                if keyword in text: #only save the text if the keyword is in the headline
                    rtnHeadlineList.append(text)
                    if len(rtnHeadlineList) == 500: 
                        breakB = True
                        break
                    break
            if breakB:
                break
        if breakB:
                break

        button = driver.find_element_by_class_name("css-vsuiox") #class outside button
        showMoreBtns = button.find_elements_by_css_selector("button") #get the button
        if len(showMoreBtns) == 0: #did not find button
            break
        showMoreBtn = showMoreBtns[0]
        if not showMoreBtn.is_enabled() or not showMoreBtn.is_displayed():
            break
        showMoreBtn.click() #click show more button

    return rtnHeadlineList

def getArticlesNYT(keywordArr, driver):
    rtnArticleList = []
    URLPage = buildURLNYT(keywordArr)
    driver.get(URLPage)
    main_window = driver.current_window_handle #save main window
    totalHeadlinesSeen = 0 #count of all headlines
    breakB = False
    past3LoopsHeadlineNumber = []
    while len(rtnArticleList) < 50: #read 50 articles total
        
        time.sleep(1)
        
        articleHeadlines = driver.find_elements_by_tag_name("h4")
        past3LoopsHeadlineNumber.append(totalHeadlinesSeen)
        if len(past3LoopsHeadlineNumber) == 4:
            past3LoopsHeadlineNumber.pop(0)
            if past3LoopsHeadlineNumber[0] == past3LoopsHeadlineNumber[1] and past3LoopsHeadlineNumber[1] == past3LoopsHeadlineNumber[2]:
                #no more headlines are being loaded
                break

        for headlineIndex in range(totalHeadlinesSeen, len(articleHeadlines)-1): #go through all headlines
            
            link = articleHeadlines[headlineIndex].find_element_by_xpath('..') #get parent
            link = link.get_attribute("href")

            if not(".com/video/" in link):
                # open new blank tab
                driver.execute_script("window.open();")

                try:
                    # switch to the new window which is second in window_handles array
                    driver.switch_to_window(driver.window_handles[1])
                except (TimeoutException, InvalidSessionIdException): #try again
                    driver.close()
                    driver.quit()
                    options = Options()
                    options.add_argument("--incognito")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                    driver.set_page_load_timeout(8)
                    time.sleep(1)
                    try:
                        driver.switch_to_window(driver.window_handles[1])
                    except (TimeoutException, InvalidSessionIdException) as e:
                        print(e)
                        break
                try:
                    driver.get(URLPage)
                except (TimeoutException, InvalidSessionIdException):
                    try:
                        driver.refresh()
                        time.sleep(1)
                    except (TimeoutException, InvalidSessionIdException):
                        print("Making new driver")
                        driver.close()
                        driver.quit()
                        options = Options()
                        options.add_argument("--incognito")
                        options.add_argument("--no-sandbox")
                        driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                        driver.set_page_load_timeout(8)
                        time.sleep(1)
                        try:
                            driver.get(URLPage)
                        except (TimeoutException, InvalidSessionIdException) as e:
                            print(e)
                            break
                        
                driver.implicitly_wait(3)
                for j in range(2): #try 2 times
                    try:
                        articlePs = driver.find_elements_by_tag_name('p')
                        pageContentStr = ""
                        for articleP in articlePs:
                            pageContentStr += articleP.text.lower() + "\n" #append all ps to large string
                        
                        for keyword in keywordArr:
                            if keyword in pageContentStr:
                                rtnArticleList.append(pageContentStr) #add to rtn list if contains a keyword
                                break
                        break #out of for loop if successful
                    except StaleElementReferenceException:
                        print("Stale element reference exception")
                
                driver.close() #close this window

            try:
                # back to the main window
                driver.switch_to_window(main_window)
            except (TimeoutException, InvalidSessionIdException):
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.switch_to_window(main_window)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break

            totalHeadlinesSeen+=1
            if len(rtnArticleList) == 50:
                breakB = True
                break
        if breakB:
            break
        
        showMoreBtn = driver.find_elements_by_xpath("//button[@type='button']") #get all the buttons
        for btn in buttons:
            if btn.text == "SHOW MORE": #get the right button
                showMoreBtn = btn
        if not showMoreBtn.is_enabled() or not showMoreBtn.is_displayed():
            break
        showMoreBtn.click() #click show more button (the 11th button)
    return rtnArticleList

def getHeadlinesWP(keywordArr, driver):
    rtnHeadlineList = []
    totalHeadlinesSeen = 0 #count of all headlines

    pageNum = 1
    breakB = False
    breakBadLoad = False
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        
        URLPage = buildURLWP(keywordArr, pageNum)
        try:
            driver.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException):
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
        
        for j in range(2): #try 2 times
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "pb-feed-item.ng-scope")))
                break
            except TimeoutException:
                print("Couldn't load page or no more results")
                driver.get(URLPage)
                time.sleep(2)
                breakBadLoad = True
        if breakBadLoad:
            break
        
        articleHeadlines = driver.find_elements_by_class_name("pb-feed-headline")
        
        for headline in articleHeadlines: #go through all headlines
            text = headline.text.lower()
            totalHeadlinesSeen+=1
            for keyword in keywordArr:
                if keyword in text: #only save the text if the keyword is in the headline
                    rtnHeadlineList.append(text)
                    if len(rtnHeadlineList) == 500: 
                        breakB = True
                        break
                    break
            if breakB:
                break
        if breakB:
            break
        
        pageNum += 1
    
    return rtnHeadlineList

def getHeadlinesDW(keywordArr, driver): #maybe load all and then look through articles?
    rtnHeadlineList = []
    URLPage = buildURLDW()
    driver.get(URLPage)
    driver.implicitly_wait(3)
    time.sleep(1)
    searchText = ""
    for keyword in keywordArr:
        searchText += keyword + " "
    searchText = searchText[:len(searchText)-1]

    driver.find_element_by_class_name("ais-SearchBox-input").send_keys(searchText)
    time.sleep(1) #wait for headlines to load

    totalHeadlinesSeen = 0 #count of all headlines
    breakB = False
    startStopCounter = False
    stopAfter3 = 0
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        
        articleHeadlines = driver.find_elements_by_tag_name("h3")

        for headlineIndex in range(totalHeadlinesSeen, len(articleHeadlines)-1): #go through all headlines
            text = articleHeadlines[headlineIndex].text.lower()
            totalHeadlinesSeen+=1
            for keyword in keywordArr:
                if keyword in text: #only save the text if the keyword is in the headline
                    rtnHeadlineList.append(text)
                    if len(rtnHeadlineList) == 500: 
                        breakB = True
                        break
                    break
            if breakB:
                break
        if breakB:
                break

        #scroll to bottom? Why do I have to reget the body every time
        body = driver.find_element_by_css_selector('body')
        body.send_keys(Keys.END)
        body.send_keys(Keys.PAGE_UP) #to register the load more

        if startStopCounter:
            stopAfter3+=1
        else:
            for j in range(2): #try 2 times
                try: #try to find the loader 2 times. If none find, start countdown.
                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "eamp66j1")))
                    startStopCounter = False
                    break
                except TimeoutException:
                    time.sleep(2)
                    startStopCounter = True
        
        if stopAfter3 == 2:
            break

    return rtnHeadlineList

def getArticlesDW(keywordArr, driver): #maybe load all and then look through articles?
    rtnArticleList = []
    URLPage = buildURLDW()
    driver.get(URLPage)
    driver.implicitly_wait(3)
    time.sleep(1)
    searchText = ""
    for keyword in keywordArr:
        searchText += keyword + " "
    searchText = searchText[:len(searchText)-1]

    driver.find_element_by_class_name("ais-SearchBox-input").send_keys(searchText)
    time.sleep(1) #wait for headlines to load

    main_window = driver.current_window_handle #save main window
    totalHeadlinesSeen = 0 #count of all headlines
    startStopCounter = False
    stopAfter3 = 0
    breakB = False
    while len(rtnArticleList) < 50: #read 50 articles total

        links = driver.find_elements_by_tag_name("a")
        links = links[7:len(links)-17]

        for linkIndex in range(totalHeadlinesSeen, len(links)-1): #go through all links after last seen ones
            link = links[linkIndex]
            link = link.get_attribute("href")
            # open new blank tab
            driver.execute_script("window.open();")

            try:
                # switch to the new window which is second in window_handles array
                driver.switch_to_window(driver.window_handles[1])
            except (TimeoutException, InvalidSessionIdException):
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.switch_to_window(driver.window_handles[1])
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break

            try:
                driver.get(link)
            except (TimeoutException, InvalidSessionIdException):
                try:
                    driver.refresh()
                    time.sleep(1)
                except (TimeoutException, InvalidSessionIdException): #try again
                    print("Making new driver")
                    driver.close()
                    driver.quit()
                    options = Options()
                    options.add_argument("--incognito")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                    driver.set_page_load_timeout(8)
                    time.sleep(1)
                    try:
                        driver.get(link)
                    except (TimeoutException, InvalidSessionIdException) as e:
                        print(e)
                        break
            for j in range(2): #try 2 times
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "css-1yvgfcr")))
                    #wait until page is loaded (looking for date class -- on every article)
                    for i in range(3):
                        try:
                            articlePs = driver.find_elements_by_tag_name('p')
                            pageContentStr = ""
                            for articleP in articlePs:
                                pageContentStr += articleP.text + "\n" #append all ps to large string
                            for keyword in keywordArr:
                                if keyword in pageContentStr:
                                    rtnArticleList.append(pageContentStr) #add to rtn list if contains a keyword
                                    break
                            break #out of for loop if successful
                        except StaleElementReferenceException:
                            print("Stale element reference exception")
                    break #out of for loop if successful
                except TimeoutException:
                    print("Couldn't load page")
            
            driver.close() #close this window
            try:
                driver.switch_to_window(main_window) #back to the main window
            except (TimeoutException, InvalidSessionIdException):
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.switch_to_window(main_window)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
            
            totalHeadlinesSeen+=1
            if len(rtnArticleList) == 50:
                breakB = True
                break
        if breakB:
            break
        
        #scroll to bottom? Why do I have to reget the body every time
        body = driver.find_element_by_css_selector('body')
        body.send_keys(Keys.END)
        body.send_keys(Keys.PAGE_UP) #to register the load more

        if startStopCounter:
            stopAfter3+=1
        else:
            for j in range(2): #try 2 times
                try: #try to find the loader 3 times. If none find, start countdown.
                    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "eamp66j1")))
                    startStopCounter = False
                    break
                except TimeoutException:
                    startStopCounter = True
        
        if stopAfter3 == 2:
            break

    return rtnArticleList

def getArticlesFOX(keywordArr, driver):
    rtnArticleList = []
    URLPage = buildURLFOX(keywordArr)
    driver.get(URLPage)
    driver.implicitly_wait(5)
    main_window = driver.current_window_handle #save main window
    totalHeadlinesSeen = 0 #count of all headlines
    breakB = False
    past3LoopsHeadlineNumber = []
    while len(rtnArticleList) < 50: #read 50 articles total

        time.sleep(1)
        
        articleHeadlines = driver.find_elements_by_class_name("title")
        articleHeadlines = articleHeadlines[3:len(articleHeadlines)-1] #get relevant to articles

        past3LoopsHeadlineNumber.append(totalHeadlinesSeen)
        if len(past3LoopsHeadlineNumber) == 4:
            past3LoopsHeadlineNumber.pop(0)
            if past3LoopsHeadlineNumber[0] == past3LoopsHeadlineNumber[1] and past3LoopsHeadlineNumber[1] == past3LoopsHeadlineNumber[2]:
                #no more headlines are being loaded
                break

        for headlineIndex in range(totalHeadlinesSeen, len(articleHeadlines)-1): #go through all headlines

            link = articleHeadlines[headlineIndex].find_element_by_css_selector("a") #get link in title
            link = link.get_attribute("href")

            if not("/v/" in link):
                # open new blank tab
                driver.execute_script("window.open();")

                try:
                    # switch to the new window which is second in window_handles array
                    driver.switch_to_window(driver.window_handles[1])
                except (TimeoutException, InvalidSessionIdException): #try again
                    driver.close()
                    driver.quit()
                    options = Options()
                    options.add_argument("--incognito")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                    driver.set_page_load_timeout(8)
                    time.sleep(1)
                    try:
                        driver.switch_to_window(driver.window_handles[1])
                    except (TimeoutException, InvalidSessionIdException) as e:
                        print(e)
                        break

                try:
                    driver.get(link)
                except (TimeoutException, InvalidSessionIdException):
                    try:
                        driver.refresh()
                        time.sleep(1)
                    except (TimeoutException, InvalidSessionIdException):
                        print("Making new driver")
                        driver.close()
                        driver.quit()
                        options = Options()
                        options.add_argument("--incognito")
                        options.add_argument("--no-sandbox")
                        driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                        driver.set_page_load_timeout(8)
                        time.sleep(1)
                        try:
                            driver.get(link)
                        except (TimeoutException, InvalidSessionIdException) as e:
                            print(e)
                            break
                for j in range(2): #try 2 times
                    try:
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "headline")))
                        #wait until page is loaded (on every article)
                        for i in range(2):
                            try:
                                articlePs = driver.find_elements_by_tag_name('p')
                                pageContentStr = ""
                                for articleP in articlePs:
                                    pageContentStr += articleP.text.lower() + "\n" #append all ps to large string
                                
                                for keyword in keywordArr:
                                    if keyword in pageContentStr:
                                        rtnArticleList.append(pageContentStr) #add to rtn list if contains a keyword
                                        break
                                break #out of for loop if successful
                            except StaleElementReferenceException:
                                print("Stale element reference exception")
                        break #out of loop if successful
                    except TimeoutException:
                        print("Couldn't load page")
                
                driver.close() #close this window

                # back to the main window
                try:
                    driver.switch_to_window(main_window)
                except (TimeoutException, InvalidSessionIdException): #try again
                    driver.close()
                    driver.quit()
                    options = Options()
                    options.add_argument("--incognito")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                    driver.set_page_load_timeout(8)
                    time.sleep(1)
                    try:
                        driver.switch_to_window(main_window)
                    except (TimeoutException, InvalidSessionIdException) as e:
                        print(e)
                        break

            totalHeadlinesSeen+=1
            if len(rtnArticleList) == 50:
                breakB = True
                break
        if breakB:
            break

        try:
            showMoreBtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "button.load-more")))
            if showMoreBtn.is_enabled() and showMoreBtn.is_displayed():
                showMoreBtn.click()
            else:
                break
        except TimeoutException:
            break
    return rtnArticleList

def getHeadlinesFOX(keywordArr, driver): #maybe load all and then look through articles?
    rtnHeadlineList = []
    URLPage = buildURLFOX(keywordArr)
    driver.get(URLPage)
    driver.implicitly_wait(5)
    totalHeadlinesSeen = 0 #count of all headlines
    past3LoopsHeadlineNumber = []
    breakB = False
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        
        time.sleep(1)

        past3LoopsHeadlineNumber.append(totalHeadlinesSeen)
        if len(past3LoopsHeadlineNumber) == 4:
            past3LoopsHeadlineNumber.pop(0)
            if past3LoopsHeadlineNumber[0] == past3LoopsHeadlineNumber[1] and past3LoopsHeadlineNumber[1] == past3LoopsHeadlineNumber[2]:
                #no more headlines are being loaded
                break

        articleHeadlines = driver.find_elements_by_class_name("title")
        articleHeadlines = articleHeadlines[3:len(articleHeadlines)-1] #get relevant to articles

        for headlineIndex in range(totalHeadlinesSeen, len(articleHeadlines)-1): #go through all headlines
            text = articleHeadlines[headlineIndex].text.lower()
            totalHeadlinesSeen+=1
            for keyword in keywordArr:
                if keyword in text: #only save the text if the keyword is in the headline
                    rtnHeadlineList.append(text)
                    if len(rtnHeadlineList) == 500: 
                        breakB = True
                        break
                    break
            if breakB:
                break
        if breakB:
                break

        try:
            showMoreBtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "button.load-more")))
            if showMoreBtn.is_enabled() and showMoreBtn.is_displayed():
                showMoreBtn.click()
            else:
                break
        except TimeoutException:
            break

    return rtnHeadlineList

def getHeadlinesHP(keywordArr, driver):
    rtnHeadlineList = []
    totalHeadlinesSeen = 0 #count of all headlines
    pageNum = 1
    driver.close()
    options = Options()
    #
    options.add_argument("--incognito")
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
    
    breakB = False
    breakBadLoad = False
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        if pageNum == 101: #max
            break

        URLPage = buildURLHP(keywordArr, pageNum)
        try:
            driver1.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver1.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException):
                driver1.close()
                driver1.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver1.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver1.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break

        for i in range(2): #try to load 2 times
            try:
                WebDriverWait(driver1, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "d-ib.mr-5.pb-10")))
                #Find the topic class = exists on pages when hp is working, but not on pages where it doesn't
                breakBadLoad = False
                break #if none work, actually could not load page
            except TimeoutException:
                print("Couldn't load page or no more results")
                driver1.get(URLPage)
                time.sleep(2)
                breakBadLoad = True
        
        if not breakBadLoad:
            articleHeadlines = driver1.find_elements_by_class_name("fz-20.lh-22.fw-b")
            
            for headline in articleHeadlines: #go through all headlines
                text = headline.text.lower()
                totalHeadlinesSeen+=1
                for keyword in keywordArr:
                    if keyword in text: #only save the text if the keyword is in the headline
                        rtnHeadlineList.append(text)
                        if len(rtnHeadlineList) == 500: 
                            breakB = True
                            break
                        break
                if breakB:
                    break
            if breakB:
                break
        else:
            driver1.close()
            options = Options()
            ua = UserAgent()
            userAgent = ua.random
            options.add_argument("--incognito")
            
            options.add_argument(f'user-agent={userAgent}')
            options.add_argument("--incognito")
            options.add_argument("--no-sandbox")
            driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)

            pageNum-=1

        pageNum+=1
        breakBadLoad = False #for next page

    return rtnHeadlineList

def getArticlesHP(keywordArr, driver):
    rtnArticleList = []
    driver.close()
    options = Options()
    #
    options.add_argument("--incognito")
    
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
    
    pageNum = 1
    breakBadLoad = False
    breakB = False
    totalHeadlinesSeen = 0
    while len(rtnArticleList) < 50: #read 50 articles total
        if pageNum == 101:
            break
        
        URLPage = buildURLHP(keywordArr, pageNum)
        try:
            driver1.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver1.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException):
                driver1.close()
                driver1.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver1.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver1.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
        main_window = driver1.current_window_handle #save main window

        for i in range(2): #try to load 3 times
            try:
                WebDriverWait(driver1, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "d-ib.mr-5.pb-10")))
                #Find the topic class = exists on pages when hp is working, but not on pages where it doesn't
                breakBadLoad = False
                break #if none work, actually could not load page
            except TimeoutException:
                print("Couldn't load page or no more results")
                driver1.get(URLPage)
                time.sleep(2)
                breakBadLoad = True

        if not breakBadLoad:
            articleHeadlines = driver1.find_elements_by_class_name("fz-20.lh-22.fw-b")
            
            for headline in articleHeadlines: #go through all headlines
                link = headline.get_attribute("href")
                totalHeadlinesSeen+=1
                driver1.execute_script("window.open();") #open new blank tab

                # switch to the new window which is second in window_handles array
                driver1.switch_to_window(driver1.window_handles[1])
                try:
                    driver1.get(link)
                except (TimeoutException, InvalidSessionIdException):
                    try:
                        driver1.refresh()
                        time.sleep(1)
                    except (TimeoutException, InvalidSessionIdException):
                        driver1.close()
                        driver1.quit()
                        options = Options()
                        options.add_argument("--incognito")
                        options.add_argument("--no-sandbox")
                        driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                        driver1.set_page_load_timeout(8)
                        time.sleep(1)
                        try:
                            driver1.get(link)
                        except (TimeoutException, InvalidSessionIdException) as e:
                            print(e)
                            break
                for j in range(2): #try 2 times
                    try:
                        WebDriverWait(driver1, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "author-card__details")))
                        #wait until page is loaded (looking for author card class -- on every article)
                        for i in range(2):
                            try:
                                articlePs = driver1.find_elements_by_tag_name('p')
                                articlePs = articlePs[:len(articlePs)-1] #remove last p
                                pageContentStr = ""
                                for articleP in articlePs:
                                    pageContentStr += articleP.text.lower() + "\n" #append all ps to large string
                                for keyword in keywordArr:
                                    if keyword in pageContentStr:
                                        rtnArticleList.append(pageContentStr) #add to rtn list if contains a keyword
                                        break
                                break #out of for loop if successful
                            except StaleElementReferenceException:
                                print("Stale element reference exception")
                        break #out of for loop if successful
                    except TimeoutException:
                        print("Couldn't load page")
                
                driver1.close() #close this window
                driver1.switch_to_window(main_window) #back to the main window

                if len(rtnArticleList) == 50:
                    breakB = True
                    break
            if breakB:
                break
        else:
            driver1.close()
            options = Options()
            ua = UserAgent()
            userAgent = ua.random
            
            options.add_argument(f'user-agent={userAgent}')
            options.add_argument("--incognito")
            options.add_argument("--no-sandbox")
            driver1 = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
            pageNum-=1

        pageNum+=1
        breakBadLoad = False #for next page

    return rtnArticleList

def getHeadlinesNYP(keywordArr, driver):
    rtnHeadlineList = []
    totalHeadlinesSeen = 0 #count of all headlines
    pageNum = 1
    breakB = False
    breakBadLoad = False
    
    while len(rtnHeadlineList) < 500: #read 500 headlines total
        URLPage = buildURLNYP(keywordArr, pageNum)
        try:
            driver.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException):
                print("Making new driver")
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
        
        for i in range(2): #try to load 3 times
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "article-loop")))
                #Find the article class - won't appear when out of articles
                breakBadLoad = False
                break #if none work, actually could not load page
            except TimeoutException:
                print("Couldn't load page or no more results")
                driver.get(URLPage)
                time.sleep(2)
                breakBadLoad = True

        articleHeadlines = driver.find_elements_by_class_name("entry-heading")
        
        for headline in articleHeadlines: #go through all headlines
            headline = headline.find_element_by_css_selector("a")
            text = headline.text.lower()
            totalHeadlinesSeen+=1
            for keyword in keywordArr:
                if keyword in text: #only save the text if the keyword is in the headline
                    rtnHeadlineList.append(text)
                    if len(rtnHeadlineList) == 500: 
                        breakB = True
                        break
                    break
            if breakB:
                break
        if breakB:
            break
    
        pageNum += 1
    
    return rtnHeadlineList

def getArticlesNYP(keywordArr, driver):
    rtnArticleList = []
    
    pageNum = 1
    breakBadLoad = False
    breakB = False
    totalHeadlinesSeen = 0
    while len(rtnArticleList) < 50: #read 50 articles total
        
        URLPage = buildURLNYP(keywordArr, pageNum)
        try:
            driver.get(URLPage)
        except (TimeoutException, InvalidSessionIdException):
            try:
                driver.refresh()
                time.sleep(1)
            except (TimeoutException, InvalidSessionIdException):
                print("Making new driver")
                driver.close()
                driver.quit()
                options = Options()
                options.add_argument("--incognito")
                options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                driver.set_page_load_timeout(8)
                time.sleep(1)
                try:
                    driver.get(URLPage)
                except (TimeoutException, InvalidSessionIdException) as e:
                    print(e)
                    break
        
        for i in range(2): #try to load 3 times
            try:
                WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "article-loop")))
                #Find the article class - won't appear when out of articles
                breakBadLoad = False
                break #if none work, actually could not load page
            except TimeoutException:
                print("Couldn't load page or no more results")
                driver.get(URLPage)
                time.sleep(2)
                breakBadLoad = True
        
        main_window = driver.current_window_handle #save main window

        if not breakBadLoad:
            articleHeadlines = driver.find_elements_by_class_name("entry-heading")
            
            for headline in articleHeadlines: #go through all headlines
                headlineA = headline.find_element_by_css_selector("a")
                link = headlineA.get_attribute("href")
                totalHeadlinesSeen+=1
                driver.execute_script("window.open();") #open new blank tab

                try:
                    # switch to the new window which is second in window_handles array
                    driver.switch_to_window(driver.window_handles[1])
                except (TimeoutException, InvalidSessionIdException): #try again
                    driver.close()
                    driver.quit()
                    options = Options()
                    options.add_argument("--incognito")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                    driver.set_page_load_timeout(8)
                    time.sleep(1)
                    try:
                        driver.switch_to_window(driver.window_handles[1])
                    except (TimeoutException, InvalidSessionIdException) as e:
                        print(e)
                        break

                try:
                    driver.get(link)
                except (TimeoutException, InvalidSessionIdException):
                    try:
                        driver.refresh()
                        time.sleep(1)
                    except (TimeoutException, InvalidSessionIdException):
                        driver.close()
                        driver.quit()
                        options = Options()
                        options.add_argument("--incognito")
                        options.add_argument("--no-sandbox")
                        driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                        driver.set_page_load_timeout(8)
                        time.sleep(1)
                        try:
                            driver.get(link)
                        except (TimeoutException, InvalidSessionIdException) as e:
                            print(e)
                            break
                for j in range(2): #try 2 times
                    try:
                        content = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "entry-content.entry-content-read-more")))
                        #wait until page is loaded (looking for author card class -- on every article)
                        for i in range(2):
                            try:
                                articlePs = content.find_elements_by_tag_name('p')
                                articlePs = articlePs[:len(articlePs)-1] #remove last p
                                pageContentStr = ""
                                for articleP in articlePs:
                                    pageContentStr += articleP.text.lower() + "\n" #append all ps to large string
                                for keyword in keywordArr:
                                    if keyword in pageContentStr:
                                        rtnArticleList.append(pageContentStr) #add to rtn list if contains a keyword
                                        break
                                break #out of for loop if successful
                            except StaleElementReferenceException:
                                print("Stale element reference exception")
                        break #out of for loop if successful
                    except TimeoutException:
                        print("Couldn't load page")
                
                driver.close() #close this window
                try:
                    driver.switch_to_window(main_window) #back to the main window
                except (TimeoutException, InvalidSessionIdException): #try again
                    driver.close()
                    driver.quit()
                    options = Options()
                    options.add_argument("--incognito")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
                    driver.set_page_load_timeout(8)
                    time.sleep(1)
                    try:
                        driver.switch_to_window(main_window) #back to the main window
                    except (TimeoutException, InvalidSessionIdException) as e:
                        print(e)
                        break

                if len(rtnArticleList) == 50:
                    breakB = True
                    break
            if breakB:
                break
        else:
            driver.close()
            options = Options()
            ua = UserAgent()
            userAgent = ua.random
            
            options.add_argument(f'user-agent={userAgent}')
            options.add_argument("--incognito")
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=".\drivers\chromedriver.exe", options=options)
            pageNum-=1

        pageNum+=1
        breakBadLoad = False #for next page

    return rtnArticleList