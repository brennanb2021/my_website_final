from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def readArticles(articles, keywords):
    sia = SentimentIntensityAnalyzer()
    rtn = {}
    
    neutralSentences = []
    negativeSentences = []
    positiveSentences = []
    neutralArticles = []
    negativeArticles = []
    positiveArticles = []
    numSentences = 0

    for article in articles:
        sentences = article.split(". ") #every sentence in each article
        sentimentSumPerArticle = 0
        numSentencesPerArticle = 0
        for sentence in sentences:
            sentenceL = sentence.lower()
            for keyword in keywords:
                if keyword in sentenceL: #does it contain a keyword
                    numSentences+=1
                    sentimentValue = det_sentence_polarity(sia, sentence)
                    if sentimentValue <= -0.05: #< or > values taken from geeksforgeeks
                        negativeSentences.append(sentence)
                    elif sentimentValue >= 0.05:
                        positiveSentences.append(sentence) #pos vs neg vs neutral sentences
                    else:
                        neutralSentences.append(sentence)
                    sentimentSumPerArticle += sentimentValue
                    numSentencesPerArticle+=1
                    break #will add sentence twice if contains both keywords
        
        negBounds = (-0.05*numSentencesPerArticle)
        posBounds = (0.05*numSentencesPerArticle)

        if sentimentSumPerArticle >= negBounds and sentimentSumPerArticle <= posBounds:
            neutralArticles.append(article)
        elif sentimentSumPerArticle < negBounds:
            negativeArticles.append(article)
        elif sentimentSumPerArticle > posBounds: #pos vs neg vs neutral articles
            positiveArticles.append(article)

    rtn["type"] = "articles"
    rtn["numArticles"] = len(articles)
    rtn["numSentences"] = numSentences

    if numSentences == 0:
        print("no sentences found")
        return False

    rtn["Negative sentences"] = (len(negativeSentences)/numSentences)*100
    rtn["negSentences"] = negativeSentences
    rtn["Neutral sentences"] = (len(neutralSentences)/numSentences)*100 #add percents to rtn
    rtn["neutSentences"] = neutralSentences
    rtn["Positive sentences"] = (len(positiveSentences)/numSentences)*100
    rtn["posSentences"] = positiveSentences
    
    rtn["Negative articles"] = (len(negativeArticles)/len(articles))*100
    rtn["Neutral articles"] = (len(neutralArticles)/len(articles))*100
    rtn["Positive articles"] = (len(positiveArticles)/len(articles))*100

    return rtn

def det_sentence_polarity(sia, sentence): #use nltk's vader lexicon to determine sentence polarity
    sentiment = sia.polarity_scores(sentence)['compound']
    return sentiment