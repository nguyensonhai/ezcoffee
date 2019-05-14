from flask import Flask, render_template, session, redirect, request
from bson import ObjectId
from pymongo import MongoClient
app = Flask(__name__)
app.secret_key = "coffehouse"
uri = 'mongodb://admin:04030211@area51-shard-00-00-ivvb1.mongodb.net:27017,area51-shard-00-01-ivvb1.mongodb.net:27017,area51-shard-00-02-ivvb1.mongodb.net:27017/test?ssl=true&replicaSet=Area51-shard-0&authSource=admin&retryWrites=true'
client = MongoClient(uri)
database = client.Area51m
collection_account = database['Account']
collection_categories = database['Categories']
collection_foods = database['Foods']


@app.route('/', methods=['POST', 'GET'])
def login():
    if(not 'logged_in' in session):
        if(request.method == 'GET'):
            return render_template('login.html')
        elif(request.method == 'POST'):
            form = request.form
            username = form['uname'].lower()
            password = form['psw']
            position = form['position']
            login_user = collection_account.find_one({'username': username,
                                                      'password': password,
                                                      'position': position
                                                      })
            if(login_user):
                session['_id'] = str(login_user['_id'])
                session['logged_in'] = True
                return redirect('/home')
            else:
                return render_template('login.html', check='False')
    else:
        return redirect('/home')


@app.route('/home')
def redirect_main():
    if('logged_in' in session):
        user = collection_account.find_one({'_id': ObjectId(session['_id'])})
        if(user['fullname'] == ''):
            return render_template('main.html',
                                   user=user,
                                   ps=user['position'],
                                   us=user['username'].upper()
                                   )
        else:
            return render_template('main.html',
                                   user=user,
                                   ps=user['position'],
                                   us=user['fullname']
                                   )
    else:
        return redirect('/')


@app.route('/sale')
def sale():
    if('logged_in' in session):
        foods = collection_foods.find()
        categories = collection_categories.find()
        user = collection_account.find_one({'_id': ObjectId(session['_id'])})
        return render_template('sale.html',
                                user=user,
                                categories=categories,
                                foods=foods
                                )
    else:
        return redirect('/')


@app.route('/info', methods=['GET', 'POST'])
def info():
    if('logged_in' in session):
        user = collection_account.find_one({'_id': ObjectId(session['_id'])})
        if(request.method == 'GET'):
            alert = ''
            if('alert_update' in session):
                alert = 'True'
                del session['alert_update']
            return render_template('info.html',
                                    user=user,
                                    account=user,
                                    alert=alert
                                    )
        elif(request.method == 'POST'):
            form = request.form
            username = form['username']
            password = form['password']
            fullname = form['fullname'].title()
            address = form['address']
            phone = form['phone']
            position = form['position']
            newvalues = {"$set": {'password': password,'position': position,
                                  'fullname': fullname, 'address': address,
                                  'phone': phone}}
            collection_account.update_one(user, newvalues)
            if(user['position'] != position and user['username'] == username):
                return redirect('/logout')
            else:
                session['alert_update'] = True
                return redirect('/info')
    else:
        return redirect('/')


@app.route('/manage-account')
def manage_account():
    user = collection_account.find_one({'_id': ObjectId(session['_id'])})
    if('logged_in' in session and user['position'] != 'Staff'):
        accounts = collection_account.find()
        check = 'False'
        alert = ''
        if('alert' in session):
            alert = session['alert']
            check = 'True'
            del session['alert']
        return render_template('manage_account.html',
                                user=user,
                                accounts=accounts,
                                check=check,
                                alert=alert
                                )
    else:
        return redirect('/')


@app.route('/manage-account/delete/<id>')
def delete_account(id):
    user = collection_account.find_one({'_id': ObjectId(session['_id'])})
    if('logged_in' in session and user['position'] != 'Staff'):
        delete = collection_account.find_one({'_id': ObjectId(id)})
        if(user['position'] == 'Manager' and delete['position'] == 'Admin'):
            session['alert'] = "You can not delete Admin accounts"
            return redirect('/manage-account')
        else:
            if(delete is not None):
                collection_account.delete_one(delete)
                if(user['username'] == delete['username']):
                    return redirect('/logout')
                else:
                    session['alert'] = 'Account ' + \
                        delete['username'] + ' has been deleted'
                    return redirect('/manage-account')
    else:
        return redirect('/')


@app.route('/manage-account/edit/<id>')
def edit_account(id):
    user = collection_account.find_one({'_id': ObjectId(session['_id'])})
    if('logged_in' in session and user['position'] != 'Staff'):
        edit = collection_account.find_one({'_id': ObjectId(id)})
        if(edit['position'] == 'Admin' and user['position'] == 'Manager'):
            session['alert'] = "You can not edit Admin accounts"
            return redirect('/manage-account')
        else:
            session['edit'] = id
            return redirect('/edit-account')
    else:
        return redirect('/')


@app.route('/edit-account', methods=['GET', 'POST'])
def edit():
    if('logged_in' in session):
        if('edit' in session):
            user = collection_account.find_one(
                {'_id': ObjectId(session['_id'])})
            edit = collection_account.find_one(
                {'_id': ObjectId(session['edit'])})
            if(request.method == 'GET'):
                return render_template('info.html',
                                        user=user,
                                        account=edit,
                                        check='False',
                                        alert=''
                                        )
            elif(request.method == 'POST'):
                form = request.form
                username = form['username']
                password = form['password']
                fullname = form['fullname'].title()
                address = form['address']
                phone = form['phone']
                position = form['position']
                newvalues = {"$set": {'password': password,'position': position,
                                      'fullname': fullname, 'address': address,
                                      'phone': phone}}
                collection_account.update_one(edit, newvalues)
                del session['edit']
                if(user['position'] != position and user['username'] == username):
                    return redirect('/logout')
                else:
                    session['alert'] = "Account " + \
                        username + " has been updated"
                    return redirect('/manage-account')
        else:
            return redirect('/manage-account')
    else:
        return redirect('/')


@app.route('/manage-account/addaccount', methods=['POST'])
def add_account():
    if('logged_in' in session):
        user = collection_account.find_one({'_id': ObjectId(session['_id'])})
        if(request.method == 'POST'):
            if(user['position'] != 'Staff'):
                form = request.form
                username = form['username']
                password = form['password']
                position = form['position']
                if(not collection_account.find_one({'username': username})):
                    add = {
                        'username': username.lower(),
                        'password': password,
                        'fullname': "",
                        'address': "",
                        'phone': "",
                        'position': position,
                    }
                    collection_account.insert_one(add)
                    session['alert'] = 'Added ' + position + ': ' + username
                    return redirect('/manage-account')
                else:
                    session['alert'] = 'Account ' + username + \
                        ' is already existed, please use another Usename'
                    return redirect('/manage-account')
        else:
            return redirect('/manage-account')
    else:
        return redirect('/manage-account')


@app.route('/manage-categories')
def mannage_categories():
    user = collection_account.find_one({'_id': ObjectId(session['_id'])})
    if('logged_in' in session and user['position'] != 'Staff'):
        return render_template('manage_categories.html')
    else:
        return redirect('/')


@app.route('/statistics')
def statistics():
    user = collection_account.find_one({'_id': ObjectId(session['_id'])})
    if('logged_in' in session and user['position'] != 'Staff'):
        return render_template('statistics.html')
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    del session['logged_in']
    del session['_id']
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
