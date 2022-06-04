import json
import tweepy
from flask import Flask, request, render_template, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
api_secret = json.load(open('api_secret.json'))
app.secret_key = api_secret["secret_key"]
CORS(app)


consumer_secret = json.load(open('twitter_consumer_secret.json'))
auth = tweepy.OAuthHandler(
    consumer_secret["apikey"], consumer_secret["secret"], "localhost:8000")


@app.route('/')
def index():
    # sessionがある場合
    session.parmanent = True
    if "oauth_token" in session and "oauth_verifier" in session:
        try:
            auth.request_token = {'oauth_token': session["oauth_token"],
                                  'oauth_token_secret': session["oauth_verifier"]}
            api = tweepy.API(auth)
            return render_template('index.html', tweets=api.home_timeline(count=10))
        except tweepy.errors.TooManyRequests:
            print("Too many requests")
        except tweepy.errors.TweepyException:
            session.clear()
    # sessionがない場合
    # redirectでtoken,verifierが送られてきているか確認
    oauth_verifier = request.args.get("oauth_verifier")
    oauth_token = request.args.get("oauth_token")
    # token,verifierがある場合,sessionに保存する
    if oauth_verifier:
        session["oauth_verifier"] = oauth_verifier
        session["oauth_token"] = oauth_token
        auth.get_access_token(oauth_verifier)
        api = tweepy.API(auth)
        return render_template('index.html', tweets=api.home_timeline(count=10))
    # token,verifierが無い場合,連携ボタンにauthorization_urlをレンダリングする
    return render_template('index.html', redirect_url=auth.get_authorization_url())


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
