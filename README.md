# Fen4i4 - A simple twitter bot.

[Fen4i4](https://enconn.fr/project/fenrir.php) is a twitter bot that tweet and retweet _interesting_ facts (and follow _interesting_ accounts). I want to make the bot trainable on any computer (for example a i5 2xxx and 4Gb of RAM are enough to train this bot in one night).

![Fen4i4](https://enconn.fr/images/project/fenrir/home.jpg)

# Why Fen4i4?

I just do this project for fun.

# Run your instance

I will release my classifier later. But, to run this twitter bot, you will need:

- _Tweepy_ and _Python 3_ on your computer
- (optional) A server to host the bot

## Configure the bot

You need to configure the bot with your own parameters in _config.json_. (You can get a key for twitter [here](https://apps.twitter.com/) and for discord [here](https://discordapp.com/developers/docs/topics/oauth2)). Also, you must have a classifier in `rsc`.

## Architecture

- `img/` just contains some image for <http://twitter.com/fen4i4/>
- `rsc/` will contains

  - `classifier.pickle`: the classifier
  - some files (`follow`, `nfollow`, `lastid`, `neg` and `pos`)

- `train/` will contains useful files for training the bot.

  - `classifier.pickle` if you run `train`
  - `datas/neg` and `datas/pos` to classify tweets.

## Run the bot!

```
python3 f3n414.py config_true.json

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

Init the bot...
Load classifier...
classifier loaded
Bot Ready!
H3ll0, f3n4i4
> help
Available commands:
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
>
```

# License

```
DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
        Version 2, December 2004

Copyright (C) 2016 Sébastien (AmarOk) Blin <https://enconn.fr>

Everyone is permitted to copy and distribute verbatim or modified
copies of this license document, and changing it is allowed as long
as the name is changed.

DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

0\. You just DO WHAT THE FUCK YOU WANT TO.
```

# Contribute

Please, feel free to contribute to this project in submitting patches, corrections, opening issues, etc.
