def buildURLCNN(keywordArr, pageNum):
    urlBuild = "https://www.cnn.com/search?q="
    for keyword in keywordArr:
            urlBuild += keyword + "%20"
    URL = urlBuild[:len(urlBuild)-3]

    URL = URL + "&page=1" #the page doesn't actually matter
    if pageNum != 1:
        URL = URL + "&from=" + str((pageNum)*10)

    return URL

def buildURLNYT(keywordArr):
    urlBuild = "https://www.nytimes.com/search?query="
    for keyword in keywordArr:
        urlBuild += keyword + "%20"
    urlBuild = urlBuild[:len(urlBuild)-3]
    urlBuild += "&sort=newest"
    return urlBuild

def buildURLWP(keywordArr, pageNum):
    pageNum-=1
    urlBuild = "https://www.washingtonpost.com/newssearch/?query="
    for keyword in keywordArr:
        urlBuild += keyword + "%20"
    urlBuild = urlBuild[:len(urlBuild)-3]
    urlBuild += "&sort=Date&datefilter=12%20Months"
    if pageNum != 0:
        urlBuild += "&startat=" + str(pageNum*20) + "#top"
    return urlBuild

def buildURLDW():
    urlBuild = "https://www.dailywire.com/search/news" #This source doesn't search through url
    return urlBuild

def buildURLFOX(keywordArr):
    urlBuild = "https://www.foxnews.com/search-results/search?q="
    for keyword in keywordArr:
        urlBuild += keyword + "%20"
    urlBuild = urlBuild[:len(urlBuild)-3]
    return urlBuild

def buildURLHP(keywordArr, pageNum):
    pageNum-=1
    urlBuild = "https://search.huffpost.com/search?p="
    for keyword in keywordArr:
        urlBuild += keyword + "%20"
    urlBuild = urlBuild[:len(urlBuild)-3]
    urlBuild += "&fr=huffpost&b=" + str((pageNum*10) + 1)
    return urlBuild

def buildURLNYP(keywordArr, pageNum):
    urlBuild = "https://nypost.com/search/"
    for keyword in keywordArr:
        urlBuild += keyword + "+"
    urlBuild = urlBuild[:len(urlBuild)-1]
    if pageNum != 0:
        urlBuild += "/page/" + str(pageNum) + "/"
    return urlBuild