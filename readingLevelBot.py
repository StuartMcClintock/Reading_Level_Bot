import praw
import os
import re

reddit = praw.Reddit(client_id='xIIOj6CT2smSBQ',
                     client_secret='AsmKKkWv4VOfnPZ3SWm2gVaiIEE',
                     username='OFFICER42069', password='NOT INCLUDED FOR SECURITY PURPOSES',
                     user_agent='Officer42069 patrols the internet to ensure that uncultured Reddit comments never go unnoticed')#posts=>comments

TOTAL_SAMPLES = 1000

def generateCutoffs():
    print('Calculating deciles...')
    print('''|user| (with pipes) means that user was included in the calculation,
user without pipes means that the user was attempted to be included in the calculation,
but they did not have enough comments on their account to provide a satisfactory sample''')
    levelList = []
    reviewedUsers = set()
    sub = {'funny':27680012, 'AskReddit':25637335, 'gaming':24848967, 'pics':23412531,
                  'science':22916277, 'aww':22816121, 'worldnews':22699383}

    weightDict = {}
    totVals = sum(sub.values())
    
    for key in sub.keys():
        numSamples = int(sub[key]/totVals*TOTAL_SAMPLES)
        weightDict[key] = numSamples
    
    for key in sub.keys():
        sub = reddit.subreddit(key)
        neededUsers = weightDict[key]
        foundUsers = 0
        for post in sub.hot(limit=25):
            if foundUsers == neededUsers:
                break
            for comment in post.comments:
                if foundUsers == neededUsers:
                    break
                user = post.author
                if not user.id in reviewedUsers:
                    reviewedUsers.add(user.id)
                    readingLevel = getReadingValue(user.name)
                    if readingLevel == None:
                        print(user.name)
                        continue
                    levelList.append(readingLevel)
                    print('|'+str(user.name)+'|')
                    foundUsers +=1

    outputStr = ''
    decileDist = len(levelList)/10
    levelList = sorted(levelList)
    #print(levelList)
    for i in range(0, 9):
        outputStr += str(levelList[int(i*decileDist)])+','
    outputStr = outputStr[0:len(outputStr)-1]
    file = open('cutoffs.txt', 'w')
    file.write(outputStr)
    file.close()

def countSyllables(inpt):
    numSylls = 0
    if inpt[0] in "aeiouyAEIOUY":
        numSylls += 1
    for i in range(1, len(inpt)):
        if inpt[i] in "aeiouyAEIOUY" and inpt[i-1] not in "aeiouyAEIOUY":
            numSylls += 1
    if inpt[len(inpt)-1] in "eE":
        numSylls -= 1
    if numSylls == 0:
        return 1
    return numSylls

def getReadingValue(username, timePeriod='month'):
    redditor = praw.models.Redditor(reddit, name=username)

    try:
        topComments = redditor.comments.top(timePeriod)
        topComments = list(topComments)
    except:
        ex = RuntimeError()
        ex.strerror = "The given user could not be found"
        raise ex

    #print(redditor.comment_karma)
    totalSentances = 0
    totalSyllables = 0
    totalWords = 0
    for comment in topComments:
        sentances = re.findall(r"[\w']+", comment.body)
        sentances = filter(lambda x: x!='', sentances)
        sentances = list(sentances)
        totalSentances += len(sentances)
        for sent in sentances:
            words = sent.split(" ")
            sentances = (lambda x: x!='', sentances)
            totalWords += len(words)
            for word in words:
                totalSyllables += countSyllables(word)

    if 0 in (totalSentances, totalWords):
        return None
    readingLevel = 0.39*(totalWords/totalSentances)+11.8*(totalSyllables/totalWords)
    return readingLevel

def determineRank(val, ls):
    currentIndex = 1
    for i in ls:
        if val <= i:
            return currentIndex
        currentIndex += 1
    return len(ls)

def getOrdinalString(num):
    if str(num) == '1':
        return '1st'
    elif str(num) == '2':
        return '2nd'
    elif str(num) == '3':
        return '3rd'
    else:
        return str(num)+'th'

def getReadingRank(username):
    if not os.path.exists('cutoffs.txt'):
        generateCutoffs()
    rawVal = getReadingValue(username, 'all')
    if rawVal == None:
        ex = RuntimeError()
        ex.strerror = "The user that you entered has not make enough comments to determine the reading level"
        raise ex
    file = open('cutoffs.txt')
    text = file.read()
    cutoffs = text.split(',')
    cutoffs = [int(float(i)) for i in cutoffs]
    file.close()

    rank = determineRank(rawVal, cutoffs)
    return rank

def main():
    inpt = ''
    while not inpt in ('y', 'yes', 'n', 'no'):
        inpt = input('Would you like to recalculate the cutoffs for each decile (y/n)?')
    if inpt in ('y', 'yes'):
        generateCutoffs()
    
    loop = True
    print("This program will determine the reading level of the comments of any given Reddit user")
    while loop:
        username = input("Username: ")
        try:
            rank = getReadingRank(username)
            ordinalRank = getOrdinalString(rank)
            print('The comments left by the user',username,'have a reading level in the',ordinalRank,'decile')
        except RuntimeError as e:
            print(e.strerror)

        loop = not input("Go again? (y/n):").lower() in ("n", "no")

if __name__ == "__main__":
    main()
