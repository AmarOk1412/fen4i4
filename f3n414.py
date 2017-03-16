import bs4
import datetime
import json
import os
import pickle
import random
import re
import requests
import sys
from textblob.classifiers import NaiveBayesClassifier
import time
import tweepy
from urllib.parse import urlparse

home_art = """
                                  ,--,               ,--,
                                ,--.'|             ,--.'|
.--.,                          ,--,  | :  ,--,    ,--,  | :
,--.'  \                ,---, ,---.'|  : ',--.'| ,---.'|  : '
|  | /\/            ,-+-. /  |;   : |  | ;|  |,  ;   : |  | ;
:  : :     ,---.   ,--.'|'   ||   | : _' |`--'_  |   | : _' |
:  | |-,  /     \ |   |  ,"' |:   : |.'  |,' ,'| :   : |.'  |
|  : :/| /    /  ||   | /  | ||   ' '  ; :'  | | |   ' '  ; :
|  |  .'.    ' / ||   | |  | |\   \  .'. ||  | : \   \  .'. |
'  : '  '   ;   /||   | |  |/  `---`:  | ''  : |__`---`:  | '
|  | |  '   |  / ||   | |--'        '  ; ||  | '.'|    '  ; |
|  : \  |   :    ||   |/            |  : ;;  :    ;    |  : ;
|  |,'   \   \  / '---'             '  ,/ |  ,   /     '  ,/
`--'      `----'                    '--'   ---`-'      '--'
-===========================================================-
                    A Simple Twitter B0t
-===========================================================-
"""

# Train functions


def save_classifier(classifier):
    f = open('train/classifier.pickle', 'wb')
    pickle.dump(classifier, f, -1)
    f.close()


def load_classifier():
    f = open('train/classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    return classifier


def parse_file(filename, test, train, nb):
    tweets = None
    with open('train/datas/' + filename, 'r') as f:
        tweets = f.read().split('\n')
    random.shuffle(tweets)
    cpt = 0
    for tweet in tweets:
        if cpt < nb:
            test.append((tweet, filename))
            cpt += 1
        else:
            train.append((tweet, filename))

# Bot utilities


def previously_tested(user):
    """Get accounts already tested"""
    content = ''
    with open('rsc/follow', 'r+') as f:
        content += f.read()
    content += '\n'
    with open('rsc/nfollow', 'r+') as f:
        content += f.read()
    return user in content.split('\n')


def addto(path, text):
    """Add a line to a file"""
    with open(path, 'a+') as out:
        out.write(text + '\n')


def get_web_content(command):
    """Read a web page and return (url, content)"""
    try:
        url = re.search('(?P<url>https?://[^\s]+)', command).group('url')
        r = requests.get(url)
        html = bs4.BeautifulSoup(r.text)
        return (url, html.get_text())
    except:
        return ('', '')


def replacewebsite(text):
    """Replace a link in a tweet by the title of the page"""
    try:
        url = re.search('(?P<url>https?://[^\s]+)', text).group('url')
        r = requests.get(url)
        html = bs4.BeautifulSoup(r.text)
        replacewith = html.title.text
        text = re.sub(r'https?://[^\s]+', replacewith, text)
    except:
        text = re.sub(r'https?://[^\s]+', '', text)
    return text


def clean_tweet(text):
    """Remove some characters from the tweet"""
    # TODO update this function... tweets are still ugly
    text = replacewebsite(text)
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'\\xc3\\xa[0-5]', 'a', text)
    text = re.sub(r'\\xe2\\x80\\x99', '"', text)
    text = re.sub(r'\\xc3\\xa([8-9]|[a-b])', 'e', text)
    text = re.sub(r'\\xc3\\xa([c-f])', 'i', text)
    text = re.sub(r'\\xc3\\xb[0-5]', 'o', text)
    text = re.sub(r'\\xc3\\xb([8-9]|[a-b])', 'u', text)
    text = re.sub(r'[^A-Za-z0-9(),!?\'\`]', ' ', text)
    text = re.sub(r'\'s', ' \'s', text)
    text = re.sub(r'\'ve', ' \'ve', text)
    text = re.sub(r'n\'t', ' n\'t', text)
    text = re.sub(r'\'re', ' \'re', text)
    text = re.sub(r'\'d', ' \'d', text)
    text = re.sub(r'\'ll', ' \'ll', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.replace('\\xc3\\xa7', 'c')
    text = text.replace('\\\\n', ' ')
    text = text.replace('\\\'', '\'')
    text = re.sub(r'\\\w{3}', '', text)
    text = text.lower()
    return text


def get_last_id():
    """Get the last tweet tested"""
    try:
        with open('rsc/lastid', 'r') as f:
            return int(f.read())
    except:
        return None


def set_last_id(new_id):
    """Set the last tweet tested"""
    with open('rsc/lastid', 'w+') as out:
        out.write(str(new_id))


class Bot():
    def __init__(self, config_file):
        # Initializes bot and connect to twitter
        print('Init the bot...')
        with open(config_file, 'r') as f:
            config = json.loads(f.read())
            account = config['account']
            consumer_key = config['consumer_key']
            consumer_secret = config['consumer_secret']
            access_token = config['access_token']
            access_token_secret = config['access_token_secret']
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)

            self.api = tweepy.API(auth)
            self.me = self.api.get_user(account)
            self.follow_percent = config['follow_percent']
            self.delay_min = config['delay_min']
            self.delay_max = config['delay_max']
            self.max_tweets = config['max_tweets']
            self.max_follow = config['max_follow']
            self.generate_prob = config['generate_prob']
            self.discord_webhook = config['discord_webhook']
            self.discord_username = config['discord_username']
            self.discord_avatar = config['discord_avatar']
            self.classifier_file = config['classifier']
            self.load_classifier()
        print('Bot Ready!')

    def load_classifier(self):
        """Load the classifier to sort tweets"""
        with open(self.classifier_file, 'rb') as f:
            print('Load classifier...')
            self.cl = pickle.load(f)
            print('classifier loaded')

    def eval_user(self, user, force=False, dontfollow=False):
        """Get interesting tweets from an user

        Parameters:
        - user: the screen_name of the user
        - force: if true, follow this user even if
        the classifier don't classify enough tweet
        - dontfollow: if true, don't follow the user
        """
        if previously_tested(user) and not force:
            print(user + ' already tested')
            return False
        print('Test following ' + user)
        count = 0
        userobj = self.api.get_user(user)
        # Count interesting tweets
        for tweet in self.api.user_timeline(userobj.id, count=100):
            cleaned = clean_tweet(tweet.text)
            prob_dist = self.cl.prob_classify(cleaned)
            if 'pos' in prob_dist.max():
                print(cleaned)
                addto('rsc/pos', cleaned)
                count += 1
            else:
                addto('rsc/neg', cleaned)

        # If we've got more than follow_percent % interesting tweets
        if count >= self.follow_percent:
            print('Follow: ' + user)
            if not dontfollow and user != self.me.screen_name:
                self.send_webhook('Follow: ' + user)
                self.api.create_friendship(userobj.id)
            addto('rsc/follow', user)
            return True
        else:
            print('Don\'t follow ' + user)
            addto('rsc/nfollow', user)
            return False

    def eval_followers(self, dontfollow=False):
        """Eval all followers"""
        for follower in self.api.followers(self.me.id):
            if not previously_tested(follower.screen_name):
                self.send_webhook('New follower: ' + follower.screen_name)
            self.eval_user(follower.screen_name, dontfollow=dontfollow)

    def read_lobster(self):
        r = requests.get('https://lobste.rs/')
        html = bs4.BeautifulSoup(r.text)
        links = html.find_all('span', class_='link')
        cpt = 0
        for link in links:
            aelem = link.find('a')
            if 'http' == aelem['href'][0:4]:
                print('Read: ' + aelem['href'])
                cpt += 1
                self.generate_reaction(aelem['href'])
                r = requests.get(aelem['href'])
                html = bs4.BeautifulSoup(r.text)
                try:
                    title = html.title.text
                    print(title)
                    prob_dist = self.cl.prob_classify(clean_tweet(title))
                    if 'pos' in prob_dist.max():
                        texttweet = title + " - " + aelem['href']
                        status = self.api.update_status(texttweet)
                        link = 'https://twitter.com/statuses/' + str(status.id) + ' - ' + texttweet
                        self.send_webhook('Tweet: ' + link)
                except:
                    print('except')
                if cpt > 5:
                    break

    def generate_reaction(self, tweet):
        """Generate a reaction tweet. This function get a link in a tweet,
        read the page and get if something is twittable"""
        try:
            print('GENERATING TWEET')
            text = get_web_content(tweet)
            domain = urlparse(text[0]).netloc
            print("DOMAIN:" + domain)
            possibles_tweets = []
            for line in text[1].split('\n'):
                line = line.lstrip()
                if len(line) > 0:
                    final_tweet = ''
                    result = self.cl.prob_classify(line)
                    if 'pos' == result.max():
                        if len(line) >= 120:
                            for phrase in re.split(r' *[\.\?!][\'"\)\]]* *',
                                                   line):
                                if len(phrase) < 120:
                                    result = self.cl.prob_classify(phrase)
                                    if 'pos' == result.max():
                                        final_tweet = phrase
                        else:
                            final_tweet = line
                    if final_tweet != '':
                        final_tweet = '\'' + final_tweet + '\' - ' + domain
                        if len(final_tweet) < 140:
                            print('Add: ' + final_tweet)
                            possibles_tweets.append(final_tweet)
            if len(possibles_tweets) > 0:
                random.shuffle(possibles_tweets)
                print('Send:')
                print(possibles_tweets[0])
                status = self.api.update_status(possibles_tweets[0])
                txt = self.api.get_status(status.id).text
                link = 'https://twitter.com/statuses/' + str(status.id) + ' - ' + txt
                self.send_webhook('Tweet: ' + link)
        except:
            print('An exception occurs during the generation.')
            return None

    def sleep(self):
        pause = random.randint(self.delay_min, self.delay_max)
        # simulate holiday
        if random.randint(1,120) is 1:
            pause += random.randint(1,5) * 3600 * 24
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        print(date + ': sleep ' + str(pause) + ' s')
        time.sleep(pause)

    def classify(self):
        # TODO isalreadytweet
        # (many tweet from 1 account ? Already on the same subject)
        max_rt = random.randint(1, self.max_tweets)
        cpt_follow = 0
        to_rt = []
        lastid = get_last_id()
        if 'all' in command:
            lastid = None
        set_last = True
        for tweet in self.api.home_timeline(since_id=lastid, count=250):
            cleaned = clean_tweet(tweet.text)
            prob_dist = self.cl.prob_classify(cleaned)
            if set_last:
                set_last_id(tweet.id)
                set_last = False
            if 'pos' in prob_dist.max():
                print('Add: ' + cleaned)
                userobj = tweet.user
                if random.randint(1, 3) is 1:
                    self.generate_reaction(tweet.text)

                if hasattr(tweet, 'retweeted_status'):
                    userobj = tweet.retweeted_status.author
                if cpt_follow < self.max_follow and userobj != self.me:
                    if self.eval_user(userobj.screen_name):
                        cpt_follow += 1
                if tweet.id not in to_rt and userobj != self.me:
                    to_rt.append(tweet.id)
                    addto('rsc/pos', cleaned)
                else:
                    addto('rsc/neg', cleaned)

        # Send tweets
        if len(to_rt) > 0:
            random.shuffle(to_rt)
            for tweetid in to_rt[:max_rt]:
                if 'no-rt' not in command:
                    pause = random.randint(1, 5)
                    time.sleep(pause)
                    try:
                        txt = self.api.get_status(tweetid).text
                        self.api.retweet(tweetid)
                        link = 'https://twitter.com/statuses/' + str(tweetid) + ' - ' + txt
                        self.send_webhook('Retweet: ' + link)
                    except:
                        pass

    def check_mentions(self):
        """Check new mentions"""
        lastid = get_last_id()
        mentions = self.api.mentions_timeline(since_id=lastid)
        for mention in mentions:
            txt = 'New mention from %s: %s (https://twitter.com/statuses/%i)' % (mention.user.screen_name, mention.text, mention.id)
            self.eval_user(mention.user.screen_name)
            self.send_webhook(txt)

    def send_webhook(self, content):
        """Send message to Discord"""
        data = """{
          "username":"%s",
          "icon_url":"%s",
          "content":"%s"
        }""" % (self.discord_username, self.discord_avatar, content)
        requests.post(self.discord_webhook, json=json.loads(data))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('You need to give a config file.')
        sys.exit()
    print(home_art)
    fenrir = Bot(sys.argv[1])
    print('H3ll0, f3n4i4')
    dontstop = True
    try:
        while dontstop:
            command = input('> ')
            command_first = command.split(' ')[0]
            if command_first == 'help':
                print("""Available commands:
- quit/exit: quit the app
- follow (<user>|followers): try yo follow an user or the followers of the bot
- test (<user>|followers): get interesting tweets from user or the followers
- reaction <tweet>: generate a reaction tweet
- classify: classify and retweet some tweets
- force follow <user>: follow an user
- force unfollow <user>: unfollow an user
- force unrt <id>: unretweet a tweet
- followers: get followers
- following: get following account
- mention: get mentions
- go/run: run the bot in automated mode.
- train: train a classifier
- lobster: read lobster
""")
            elif command_first == 'quit' or command_first == 'exit':
                print('Bye')
                dontstop = False
            elif command_first == 'follow' or command_first == 'test':
                userobj = None
                try:
                    user = re.search('(follow|test) (?P<user>\w+)',
                                     command).group('user')
                    if user == 'followers':
                        fenrir.eval_followers(dontfollow=(command_first == 'test'))
                    else:
                        fenrir.eval_user(user,
                                         dontfollow=(command_first == 'test'))
                except:
                    print('Can\'t detect username. Please do \'follow username\'')
            elif command_first == 'reaction':
                fenrir.generate_reaction(command)
            elif command_first == 'classify':
                fenrir.classify()
            elif command_first == 'tweet':
                totweet = command[len('tweet '):]
                if fenrir.cl.prob_classify(totweet) == 'pos':
                    print('Send tweet:' + totweet)
                    fenrir.send_webhook('Send tweet:' + totweet)
                    fenrir.api.update_status(totweet)
                else:
                    print('don\'t send this...')
            elif command_first == 'force':
                if ' follow ' in command or ' unfollow ' in command:
                    try:
                        user = re.search('force (un)?follow (?P<user>\w+)',
                                         command).group('user')
                        userobj = fenrir.api.get_user(user)
                        if ' follow ' in command:
                            fenrir.api.create_friendship(userobj.id)
                        else:
                            fenrir.api.destroy_friendship(userobj.id)
                    except:
                        print('Can\'t detect username.')
                elif 'unrt' in command:
                    try:
                        status = re.search(' unrt (?P<status>.+)',
                                           command).group('status')
                        fenrir.api.destroy_status(status)
                    except:
                        print('Can\'t detect username.')
            elif command_first == 'followers':
                for user in fenrir.api.followers(fenrir.me.id):
                    print('%s: %s' % (user.screen_name, user.description))
            elif command_first == 'following':
                for userid in fenrir.api.friends_ids(fenrir.me.id):
                    user = fenrir.api.get_user(userid)
                    print('%s: %s' % (user.screen_name, user.description))
            elif command_first == 'timeline':
                for tweet in fenrir.api.user_timeline(fenrir.me.id):
                    userobj = tweet.user
                    if hasattr(tweet, 'retweeted_status'):
                        userobj = tweet.retweeted_status.author
                    print('(%i) %s: %s' %
                          (tweet.id, userobj.screen_name, tweet.text))
            elif command_first == 'mention':
                fenrir.check_mentions()
            elif command_first == 'go' or command_first == 'run':
                while True:
                    fenrir.sleep()
                    fenrir.load_classifier()
                    fenrir.check_mentions()
                    fenrir.eval_followers()
                    fenrir.read_lobster()
                    fenrir.classify()
            elif command_first == 'lobster':
                fenrir.read_lobster()
            elif command_first == 'train':
                train = []
                testneg = []
                testpos = []
                parse_file('neg', testneg, train, 1200)
                parse_file('pos', testpos, train, 600)
                random.shuffle(train)
                print('train size: %i' % len(train))
                print('testneg size: %i' % len(testneg))
                print('testpos size: %i' % len(testpos))

                cl = None
                size = 0

                while size < len(train):
                    begin = size
                    end = size + 500
                    if end > len(train):
                        end = len(train)
                    print(str(begin) + ":" + str(end) + ":" + str(len(train)))
                    size += 500
                    if os.path.isfile('train/classifier.pickle'):
                        cl = load_classifier()
                        cl.update(train[begin:end])
                    else:
                        cl = NaiveBayesClassifier(train[begin:end])
                        save_classifier(cl)

                # Compute accuracy
                # Want > 0.95
                accuracy = cl.accuracy(testneg)
                print('Accuracy on negative: %1.8f' % accuracy)
                # Want > 0.1
                accuracy = cl.accuracy(testpos)
                print('Accuracy on positive: %1.8f' % accuracy)

                # Show 10 most informative features
                print('Best features:')
                cl.show_informative_features(10)

                #os.rename('train/classifier.pickle', 'train/classifier.pickle.2')
                ####### c/C
                #for totest in testneg:
                #    if cl.prob_classify(totest[0]) != 'neg':
                #        addto('rsc/badpos', totest[0])
                #for totest in testpos:
                #    if cl.prob_classify(totest[0]) != 'pos':
                #        addto('rsc/badneg', totest[0])
    except KeyboardInterrupt:
        print('Bye...')
