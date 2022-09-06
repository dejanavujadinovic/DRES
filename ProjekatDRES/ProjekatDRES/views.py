"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, Flask, flash, request, url_for, redirect
from ProjekatDRES import app
import socket
import time
import json
from json2html import *


host = socket.gethostname()  # as both code is running on same pc
port = 9999  # socket server port number
client_socket = socket.socket()  # instantiate
client_socket.setblocking(1)    # blocking
client_socket.connect((host, port))  # connect to the server
print('Connected to server')  # show in terminal

class Currentuser:
    sessionvariable = None

class SavedJson:
    tempjson = None

@app.route('/')
@app.route('/layout')
def layout():
    return render_template(
        'layout.html',
        title='Application',
        year=datetime.now().year,
    )


@app.route('/register', methods = ["GET", "POST"])
def register():
    notification = None
    try:
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            name = request.form['name']
            lastname = request.form['lastname']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            telephone = request.form['telephone']
            securitycode = request.form['securitycode']
            if Currentuser.sessionvariable != None:
                message = "logout;{}".format(Currentuser.sessionvariable)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response

            message = "register;{};{};{};{};{};{};{};{};{}".format(email, password, name, lastname, address, city, state, telephone, securitycode)
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response

            if data == "success":
                Currentuser.sessionvariable = email
                notification = "Successfully logged in!"
                return render_template("layout.html", notification = notification)
            elif data=="userexists":
                notification = "That email is used by someone else!"
                return render_template("register.html", notification = notification)
    
    except Exception as e:
        flash(e)
        return render_template("login.html", notification = notification)

    if request.method == "POST":
        return render_template("layout.html", notification = notification)
    else:
        return render_template("register.html", notification = None)

@app.route('/login', methods = ["GET", "POST"])
def login():
    print(Currentuser.sessionvariable)
    notification = None
    try:
        if request.method == "POST":
            attempted_mail = request.form['email']
            attempted_password = request.form['password']
            if Currentuser.sessionvariable != None and Currentuser.sessionvariable != attempted_mail:
                message = "logout;{}".format(Currentuser.sessionvariable)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response

            message = "login;{};{}".format(attempted_mail, attempted_password)
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response
            
            if data == "success":
                Currentuser.sessionvariable = attempted_mail
                notification = "Successfully logged in!"
                return render_template("layout.html", notification = notification)
            elif data == "alreadyloggedin" and Currentuser.sessionvariable == None:
                notification = "User with that credentials is already logged on other client!"
            elif data == "alreadyloggedin":
                notification = "You are already logged in!"
            elif data == "fail":
                notification = "Please logout first!"
            elif data == "usernotexist":
                notification = "Email or password incorrect!"
            return render_template("login.html", notification = notification)

    except Exception as e:
        flash(e)
        return render_template("login.html", notification = notification)
    
    if request.method == "POST":
        return render_template("layout.html", notification = notification)
    else:
        return render_template("login.html", notification = None)
    

@app.route('/logout')
def logout():
        notification = None
        message = "logout;{}".format(Currentuser.sessionvariable)
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        if data == "loggedout":
            Currentuser.sessionvariable = None
            notification = "Successfully logged out!"
        else:
            notification = "You weren't logged in!"
            Currentuser.sessionvariable = None
        return render_template("layout.html", notification = notification)


@app.route('/editprofile', methods = ["GET", "POST"])
def editprofile():
    notification = None
    try:
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            name = request.form['name']
            lastname = request.form['lastname']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            telephone = request.form['telephone']
            
            message = "editprofile;{};{};{};{};{};{};{};{};{}".format(Currentuser.sessionvariable ,email, password, name, lastname, address, city, state, telephone)
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response

            if data == "success":
                Currentuser.sessionvariable = email
                notification = "Successfully updated profile!"
            if data == "userexists":
                notification = "Username already exists!"
            if data == "notevenlogged":
                notification = "Please log in to proceed!"
            return render_template("editprofile.html", notification = notification)
    except Exception as e:
        flash(e)
        return render_template("editprofile.html", notification = notification)

    if request.method == "POST":
        return render_template("layout.html", notification = notification)
    else:
        return render_template("editprofile.html", notification = None)


@app.route('/cardbalance')
def cardbalance():
        notification = None
        balance = ""
        message = "cardbalance;{}".format(Currentuser.sessionvariable)
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        if data == "notevenlogged":
            notification = "Please log in to proceed!"
        elif data == "userprofilenotactivated":
            notification = "Profile not activated!"
        else:
            notification = "Your card balance: "
            balance = data
        return render_template("cardbalance.html", notification = notification, balance = balance)



@app.route('/verification', methods = ["GET", "POST"])
def verification():
        notification = None
        try:
            if request.method == "POST":
                notification = None
                number = request.form['number']
                message = "verification;{};{}".format(Currentuser.sessionvariable, number)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response
                if data == "alreadyactivated":
                    Currentuser.sessionvariable == None
                    notification = "Your account is already activated!"
                elif data == "notevenlogged":
                    notification = "Please sign in to proceed!"
                elif data == "success":
                    notification = "Successfully activated account"
                elif data == "wrongcard":
                    notification = "You entered wrong card!"
                return render_template("verification.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("verification.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("verification.html", notification = None)




@app.route('/depositonline', methods = ["GET", "POST"])
def depositonline():
        notification = None
        try:
            if request.method == "POST":
                notification = None
                currency = request.form['currency']
                amount = request.form['amount']
  
                message = "depositonline;{};{};{}".format(Currentuser.sessionvariable, currency, amount)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response
                if data == "notevenlogged":
                    notification = "Please log in to proceed!"
                if data == "notenoughmoney":
                    notification = "You dont have enough money!"
                elif data == "userprofilenotactivated":
                    notification = "Please sign in to proceed!"
                elif data == "success":
                    notification = "Successfully deposited online!"
                return render_template("depositonline.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("depositonline.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("depositonline.html", notification = None)




@app.route('/banktransaction', methods = ["GET", "POST"])
def banktransaction():
        notification = None
        try:
            if request.method == "POST":
                notification = None
                reciever = request.form['reciever']
                amount = request.form['amount']
  
                message = "transactionbank;{};{};{}".format(Currentuser.sessionvariable, reciever, amount)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response
                if data == "notevenlogged":
                    notification = "Please log in to proceed!"
                if data == "notenoughmoney":
                    notification = "You dont have enough money!"
                elif data == "userprofilenotactivated":
                    notification = "Please sign in to proceed!"
                elif data == "success":
                    notification = "Transaction is ongoing!"
                elif data == "userdoesnotexist":
                    notification = "User not found!"
                return render_template("banktransaction.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("banktransaction.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("banktransaction.html", notification = None)



@app.route('/onlinetransaction', methods = ["GET", "POST"])
def onlinetransaction():
        notification = None
        try:
            if request.method == "POST":
                notification = None
                reciever = request.form['reciever']
                amount = request.form['amount']
                currency = request.form['currency']
  
                message = "onlinetransaction;{};{};{};{}".format(Currentuser.sessionvariable, reciever, amount, currency)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response
                if data == "notevenlogged":
                    notification = "Please log in to proceed!"
                if data == "notenoughmoney":
                    notification = "You dont have enough money!"
                elif data == "userprofilenotactivated":
                    notification = "Please sign in to proceed!"
                elif data == "success":
                    notification = "Transaction is ongoing!"
                elif data == "userdoesnotexist":
                    notification = "User not found!"
                return render_template("onlinetransaction.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("onlinetransaction.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("onlinetransaction.html", notification = None)



@app.route('/exchange', methods = ["GET", "POST"])
def exchange():
        notification = None
        try:
            if request.method == "POST":
                notification = None
                fromCurrency = request.form['fromCurrency']
                toCurrency = request.form['toCurrency']
                amount = request.form['amount']
                
                message = "exchange;{};{};{};{}".format(Currentuser.sessionvariable, fromCurrency, toCurrency, amount)
                client_socket.send(message.encode())  # send message
                data = client_socket.recv(1024).decode()  # receive response
                if data == "notevenlogged":
                    notification = "Please log in to proceed!"
                if data == "notenoughmoney":
                    notification = "You dont have enough money!"
                elif data == "userprofilenotactivated":
                    notification = "Please sign in to proceed!"
                elif data == "success":
                    notification = "Exchange commpleted!"
                return render_template("exchange.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("exchange.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("exchange.html", notification = None)



@app.route('/viewbankhistory', methods = ["GET", "POST"])
def viewbankhistory():
        notification = None
        try:
            if request.method == "GET":
                notification = None
                message = "viewbankhistory;{}".format(Currentuser.sessionvariable)
                client_socket.send(message.encode())  # send message
                data = "";
                client_socket.setblocking(0)
                while True:
                    try:
                        time.sleep(2)
                        data += client_socket.recv(1024).decode()
                        pass
                    except:
                        if data == "":
                            continue
                        break
                client_socket.setblocking(1)
                if data == "notevenlogged":
                    notification = "Please log in to proceed!"
                elif data == "userprofilenotactivated":
                    notification = "Please activate profile to proceed!"
                else:
                    json_data = json.loads(data)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                return render_template("viewbankhistory.html", notification = notification)
            
            elif request.method == "POST":
                notification = None
                order = request.form['order']
                number = request.form['number']
                sender = request.form['sender']
                reciever = request.form['reciever']
                amount = request.form['amount']
                
                if order == "Number-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["number"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Number-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["number"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Sender-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["sender"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Sender-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["sender"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Reciever-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["reciever"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Reciever-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["reciever"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table

                elif order == "Amount-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["din"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Amount-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["din"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table

                elif order == "":
                    json_data = SavedJson.tempjson
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                json_data = SavedJson.tempjson
                if number != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['number']) == str(number)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table

                if sender != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['sender']) == str(sender)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table

                if reciever != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['reciever']) == str(reciever)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table
                
                if amount != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['din']) == str(amount)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table
                return render_template("viewbankhistory.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("viewbankhistory.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("viewbankhistory.html", notification = None)


@app.route('/viewonlinehistory', methods = ["GET", "POST"])
def viewonlinehistory():
        notification = None
        try:
            if request.method == "GET":
                notification = None
                message = "viewonlinehistory;{}".format(Currentuser.sessionvariable)
                client_socket.send(message.encode())  # send message
                data = "";
                client_socket.setblocking(0)
                while True:
                    try:
                        time.sleep(2)
                        data += client_socket.recv(1024).decode()
                        pass
                    except:
                        if data == "":
                            continue
                        break
                client_socket.setblocking(1)
                if data == "notevenlogged":
                    notification = "Please log in to proceed!"
                elif data == "userprofilenotactivated":
                    notification = "Please activate profile to proceed!"
                else:
                    json_data = json.loads(data)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                return render_template("viewonlinehistory.html", notification = notification)
            
            elif request.method == "POST":
                notification = None
                order = request.form['order']
                number = request.form['number']
                sender = request.form['sender']
                reciever = request.form['reciever']
                amount = request.form['amount']
                currency = request.form['currency']
                
                if order == "Number-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["number"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Number-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["number"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Sender-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["sender"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Sender-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["sender"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Reciever-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["reciever"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Reciever-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["reciever"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table

                elif order == "Amount-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["amount"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Amount-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["amount"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table

                elif order == "Currency-Ascend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["currency"])
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                elif order == "Currency-Descend":
                    json_data = SavedJson.tempjson
                    json_data.sort(key = lambda x:x["currency"], reverse = True)
                    SavedJson.tempjson = json_data
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table

                elif order == "":
                    json_data = SavedJson.tempjson
                    formatted_table = json2html.convert(json = json_data)
                    notification = formatted_table
                
                json_data = SavedJson.tempjson
                if number != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['number']) == str(number)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table

                if sender != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['sender']) == str(sender)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table

                if reciever != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['reciever']) == str(reciever)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table
                
                if amount != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(int(x['amount'])) == str(amount)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table

                if currency != "":
                    input_dict = json_data
                    if input_dict != "[]":
                        output_dict = [x for x in input_dict if str(x['currency']) == str(currency)]
                        json_data = json.dumps(output_dict)
                        json_data = json.loads(json_data)
                    formatted_table = json2html.convert(json = json_data)        
                    notification = formatted_table
                return render_template("viewonlinehistory.html", notification = notification)

        except Exception as e:
            flash(e)
            return render_template("viewonlinehistory.html", notification = notification)
    
        if request.method == "POST":
            return render_template("layout.html", notification = notification)
        else:
            return render_template("viewonlinehistory.html", notification = None)



