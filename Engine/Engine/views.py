"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from Engine import app
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
import socket
import sys
sys.path.append('..\DAO')
import DatabaseFile
import _thread
import time
from forex_python.converter import CurrencyRates
from multiprocessing import Process

class Connections:
    listconnections = []

class UserSession:
    userlist = []




def wait_connection():
    # get the hostname
    host = socket.gethostname()
    port = 9999
    server_socket = socket.socket() 
    server_socket.bind((host, port))
    server_socket.setblocking(0)
    server_socket.listen(5)
    while True:
        try:
            conn, address = server_socket.accept()
            print("New connection: " + str(address))
            Connections.listconnections.append((conn, address))
        except:
            time.sleep(1)


def server_program():
    _thread.start_new(wait_connection, ())
    while True:
        for client in Connections.listconnections:
           try:
                data = client[0].recv(1024).decode()
                if not data:
                    break
                values = data.split(";")
                #######################################################################################     #LOGIN
                if values[0] == "login":
                     var = DatabaseFile.DatabaseClass().TryLogin(values[1], values[2])
                     if var:
                         if values[1] not in UserSession.userlist:
                             UserSession.userlist.append(values[1])
                             retval = "success"
                         elif values[1] in UserSession.userlist:            
                             retval = "alreadyloggedin"
                     else:
                         retval = "usernotexist"
                     client[0].send(retval.encode())
                #######################################################################################     #REGISTER
                if values[0] == "register":
                    var = DatabaseFile.DatabaseClass().UserExists(values[1])
                    if var:
                        retval = "userexists"                                                               
                    else:
                        DatabaseFile.DatabaseClass().StoreUser(values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8])
                        DatabaseFile.DatabaseClass().CreateBankAccount(values[1], values[9])
                        UserSession.userlist.append(values[1]) 
                        retval = "success"
                    client[0].send(retval.encode())
                #######################################################################################     #LOGOUT
                if values[0] == "logout":
                    if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                    elif values[1] in UserSession.userlist:                  
                        UserSession.userlist.remove(values[1])
                        retval = "loggedout"
                    client[0].send(retval.encode())
                #######################################################################################     #EDIT PROFILE
                if values[0] == "editprofile":
                    if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                    elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().UserExists(values[2])
                        if var:
                            retval = "userexists"
                        else:
                            retval = "success"
                            UserSession.userlist.remove(values[1])
                            UserSession.userlist.append(values[2])
                            DatabaseFile.DatabaseClass().UpdateCards(values[1], values[2])
                            DatabaseFile.DatabaseClass().UpdateUser(values[1] ,values[2], values[3], values[4], values[5], values[6], values[7], values[8], values[9])
                            DatabaseFile.DatabaseClass().EditProfileUpdateAccounts(values[1], values[2])
                    client[0].send(retval.encode())
                #######################################################################################     #CARD BALANCE PROFILE
                if values[0] == "cardbalance":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().GetCardBalance(values[1])
                        if var == "userprofilenotactivated":
                            retval = "userprofilenotactivated"
                        else:
                            retval = str(var)
                     client[0].send(retval.encode())
                #######################################################################################     #VERIFICATION
                if values[0] == "verification":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            retval = "alreadyactivated"
                        else:
                            retval = DatabaseFile.DatabaseClass().ActivateAccount(values[1], values[2])
                     client[0].send(retval.encode())
                #######################################################################################     #DEPOSTI ONLINE
                if values[0] == "depositonline":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            if DatabaseFile.DatabaseClass().EnoughMoney(values[1], values[3]):
                                DatabaseFile.DatabaseClass().RemoveMoneyFromCard(values[1], values[3])
                                if not DatabaseFile.DatabaseClass().HasThatCurrency(values[1], values[2]):
                                    DatabaseFile.DatabaseClass().AddNewAccount(values[1], values[2], values[3])
                                else:
                                    DatabaseFile.DatabaseClass().UpdateAccount(values[1], values[2], values[3])
                                retval = "success"
                            else:
                                retval = "notenoughmoney"
                        else:
                            retval = "userprofilenotactivated"
                     client[0].send(retval.encode())
                #######################################################################################     #BANK TRANSACTION
                if values[0] == "transactionbank":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            var = DatabaseFile.DatabaseClass().UserExistByNumberOrMail(values[2])
                            if var:
                                if DatabaseFile.DatabaseClass().EnoughMoney(values[1], values[3]):
                                    p = Process(target = banktransactionprocess, args=(values[1], values[2], values[3]))
                                    p.start()
                                    retval = "success"
                                else:
                                    retval = "notenoughmoney"
                            else:
                                retval = "userdoesnotexist"
                        else:
                            retval = "userprofilenotactivated"
                     client[0].send(retval.encode())
                     if retval != success:
                         print("********************************")
                         print("Transaction state: DECLINED    *")
                         print("********************************")
                #######################################################################################     #ONLINE TRANSACTION
                if values[0] == "onlinetransaction":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            var = DatabaseFile.DatabaseClass().UserExistInCardsByEmail(values[2])
                            if var:
                                var = DatabaseFile.DatabaseClass().EnoughOfSpecifiedCurrency(values[1], values[3], values[4])
                                if var:
                                    p = Process(target = onlinetransactionprocess, args=(values[1], values[2], values[3], values[4]))
                                    p.start()
                                    retval = "success"
                                else:
                                    retval = "notenoughmoney"
                            else:
                                var = DatabaseFile.DatabaseClass().UserExistInCardsByNumber(values[2])
                                if var:
                                    reciever = DatabaseFile.DatabaseClass().GetEmailFromUserByCardNumber(values[2])
                                    var = DatabaseFile.DatabaseClass().EnoughOfSpecifiedCurrency(values[1], values[3], values[4])
                                    if var:
                                        p = Process(target = onlinetransactionprocess, args=(values[1], reciever, values[3], values[4]))
                                        p.start()
                                        retval = "success"
                                    else:
                                        retval = "notenoughmoney"
                                else:
                                    retval = "userdoesnotexist"
                        else:
                            retval = "userprofilenotactivated"
                     client[0].send(retval.encode())
                     if retval != success:
                        print("********************************")
                        print("Transaction state: DECLINED    *")
                        print("********************************")
                #######################################################################################     #EXCHANGE OFFICE
                if values[0] == "exchange":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            if DatabaseFile.DatabaseClass().HasThatCurrency(values[1], values[2]):
                                if DatabaseFile.DatabaseClass().EnoughOfSpecifiedCurrency(values[1], values[4], values[2]):
                                    DatabaseFile.DatabaseClass().MakeExchange(values[1], values[2], values[3], values[4])
                                    retval = "success"
                                else:
                                    retval = "notenoughmoney"
                            else:
                                retval = "notenoughmoney"
                        else:
                            retval = "userprofilenotactivated"
                     client[0].send(retval.encode())
                #######################################################################################     #VIEW BANK HISTORY
                if values[0] == "viewbankhistory":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            retval = DatabaseFile.DatabaseClass().GetBankHistory(values[1])
                        else:
                            retval = "userprofilenotactivated"
                     client[0].send(bytes(retval, encoding="utf-8"))
                #######################################################################################     #VIEW ONLINE HISTORY
                if values[0] == "viewonlinehistory":
                     if values[1] not in UserSession.userlist:
                        retval = "notevenlogged"
                     elif values[1] in UserSession.userlist:
                        var = DatabaseFile.DatabaseClass().IsActivated(values[1])
                        if var == "alreadyactivated":
                            retval = DatabaseFile.DatabaseClass().GetOnlineHistory(values[1])
                        else:
                            retval = "userprofilenotactivated"
                     client[0].send(bytes(retval, encoding="utf-8"))
           except:
               pass
    client[1].close()
#######################################################################################################


def banktransactionprocess(sender, reciever, amount):
    print("********************************")
    print("Transaction state: ONGOING     *")
    print("********************************")
    time.sleep(120)
    DatabaseFile.DatabaseClass().RemoveMoneyFromCard(sender, amount)
    DatabaseFile.DatabaseClass().AddMoneyToCard(reciever, amount)
    DatabaseFile.DatabaseClass().AddBankTransactionHistory(sender, reciever, amount)
    print("********************************")
    print("Transaction state: COMPLETED   *")
    print("********************************")


def onlinetransactionprocess(sender, reciever, amount, currency):
    print("********************************")
    print("Transaction state: ONGOING     *")
    print("********************************")
    time.sleep(120)
    DatabaseFile.DatabaseClass().RemoveMoneyFromAccount(sender, amount, currency)
    if not DatabaseFile.DatabaseClass().HasThatCurrency(reciever, currency):
        DatabaseFile.DatabaseClass().AddNewAccountOnline(reciever, currency, amount,)
    else:
        DatabaseFile.DatabaseClass().UpdateAccountOnline(reciever, currency, amount)
    DatabaseFile.DatabaseClass().AddOnlineTransactionHistory(sender, reciever, amount, currency,)
    print("********************************")
    print("Transaction state: COMPLETED   *")
    print("********************************")


@app.route('/')
@app.route('/home')
def home():
    _thread.start_new(server_program, ())
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )


