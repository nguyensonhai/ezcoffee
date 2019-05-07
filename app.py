from flask import Flask, render_template, session, redirect, request
from bson import ObjectId
from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "film4u"
uri = 'mongodb://admin:04030211@film4u-shard-00-00-mjqak.mongodb.net:27017,film4u-shard-00-01-mjqak.mongodb.net:27017,film4u-shard-00-02-mjqak.mongodb.net:27017/test?ssl=true&replicaSet=film4u-shard-0&authSource=admin&retryWrites=true'
client = MongoClient(uri)
database = client.film4u
collection_account = database['Account']


@app.route('/', methods=['POST', 'GET'])
def login():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
