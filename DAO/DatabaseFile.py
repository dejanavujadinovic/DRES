import mysql.connector
from datetime import datetime
import time
from forex_python.converter import CurrencyRates
import json

class DatabaseClass:
    def __init__(self):
        self = self
    
    def rsdtoeur(self, sum):
        return sum / 117

    def eurtorsd(self, sum):
        return sum * 117        

    def TryLogin(self, email, password):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email , password))
        myresult = mycursor.fetchall()
        return myresult

    def UserExists(self, email):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        myresult = mycursor.fetchall()
        return myresult

    def StoreUser(self, email, password, name, lastname, address, city, state, telephone):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("INSERT INTO users (email, password, name, lastname, address, city, state, telephone) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (email, password, name, lastname, address, city, state, telephone,))
        database.commit()

    def UpdateUser(self, currentEmail, email, password, name, lastname, address, city, state, telephone):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        activated = self.IsActivated(currentEmail)
        if activated == "alreadyactivated":
            value = 1
        else:
            value = 0
        
        mycursor.execute("DELETE FROM users WHERE email = %s", (currentEmail,))
        mycursor.execute("INSERT INTO users (email, password, name, lastname, address, city, state, telephone, activated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (email, password, name, lastname, address, city, state, telephone, value,))
        database.commit()
    
    def CreateBankAccount(self, email, securitycode):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT COUNT(*) FROM cards")
        res = mycursor.fetchone()
        number = res[0] + 4000 + 1
        cardnumber = str(number) + str(number) + str(number) + str(number)
        expiringdate = datetime.now()
        expiringdate = expiringdate.replace(year=expiringdate.year + 2)
        formatted_date = expiringdate.strftime('%Y-%m-%d %H:%M:%S')
        mycursor.execute("INSERT INTO cards (number, email, expiringdate, securitycode, din) VALUES(%s, %s, %s, %s, %s)", (cardnumber, email, formatted_date, securitycode, 0,))
        database.commit()

    def GetCardBalance(self, mail):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT activated FROM users WHERE email = %s", (mail,))
        res = mycursor.fetchone()
        if not res[0]:
            retval = "userprofilenotactivated"
            return retval
        else:
            mycursor.execute("SELECT din FROM cards WHERE email = %s", (mail,))
            res = mycursor.fetchone()
            return res[0]

    def IsActivated(self, mail):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT activated FROM users WHERE email = %s", (mail,))
        res = mycursor.fetchone()
        if res[0]:
            retval = "alreadyactivated"
        else:
            retval = "notactive"
        return retval

    def ActivateAccount(self, mail, number):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM cards WHERE email = %s AND number = %s", (mail, number,))
        myresult = mycursor.fetchall()
        if not myresult:
            return "wrongcard"
        mycursor.execute("UPDATE users SET activated = '1' WHERE email = %s", (mail,))
        database.commit()
        dinari = self.GetCardBalance(mail)
        euro = CurrencyRates().convert('USD', 'EUR', 1)
        dinari = dinari - self.eurtorsd(euro)
        mycursor.execute("UPDATE cards SET din = %s WHERE email = %s", (dinari, mail,))
        database.commit()
        return "success"

    def UpdateCards(self, old, new):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("UPDATE cards SET email = %s WHERE email = %s", (new, old,))
        database.commit()

    def RemoveMoneyFromCard(self, mail, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        dinari = self.GetCardBalance(mail)
        value = int(dinari) - int(amount)
        mycursor.execute("UPDATE cards SET din = %s WHERE email = %s", (value, mail,))
        database.commit()

    def EnoughMoney(self, mail, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT din FROM cards WHERE email = %s", (mail,))
        res = mycursor.fetchone()
        if res[0] > int(amount):
            return True
        else:
            return False

    def HasThatCurrency(self, mail, currency):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM accounts WHERE email = %s AND currency = %s", (mail, currency,))
        myresult = mycursor.fetchall()
        if myresult:
            return True
        else:
            return False

    def AccountNumber(self):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT COUNT(*) FROM accounts")
        res = mycursor.fetchone()
        number = res[0] + 1
        return number

    def AddNewAccount(self, mail, currency, amount):
        number = self.AccountNumber()
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        euri = self.rsdtoeur(float(amount))
        balance = CurrencyRates().convert('EUR', currency, euri)
        mycursor.execute("INSERT INTO accounts (number, email, amount, currency) VALUES(%s, %s, %s, %s)", (number, mail, balance, currency,))
        database.commit()

    def GetAccountBalance(self, mail, currency):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT amount FROM accounts WHERE email = %s AND currency = %s", (mail, currency,))
        res = mycursor.fetchone()
        return res[0]

    def UpdateAccount(self, mail, currency, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        oldBalance = self.GetAccountBalance(mail, currency)
        euri = self.rsdtoeur(float(amount))
        newBalance = float(oldBalance) + CurrencyRates().convert('EUR', currency, euri)
        mycursor.execute("UPDATE accounts SET amount = %s WHERE email = %s AND currency = %s", (newBalance, mail, currency,))
        database.commit()

    def EditProfileUpdateAccounts(self, oldUser, newUser):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("UPDATE accounts SET email = %s WHERE email = %s", (newUser, oldUser,))
        database.commit()


    def AddMoneyToCard(self, user, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT din FROM cards WHERE email = %s or number = %s", (user, user,))
        res = mycursor.fetchone()
        balance = int(amount) + res[0]
        mycursor.execute("UPDATE cards SET din = %s WHERE email = %s or number = %s", (balance, user, user,))
        database.commit()

    def BankHistoryNumber(self):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT COUNT(*) FROM bankhistory")
        res = mycursor.fetchone()
        number = res[0] + 1
        return number

    def AddBankTransactionHistory(self, sender, reciever, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        number = self.BankHistoryNumber()
        mycursor.execute("INSERT INTO bankhistory (number, sender, reciever, din) VALUES(%s, %s, %s, %s)", (number, sender, reciever, amount,))
        database.commit()

    def UserExistByNumberOrMail(self, user):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM cards WHERE email = %s or number = %s", (user, user,))
        myresult = mycursor.fetchall()
        return myresult

    def EnoughOfSpecifiedCurrency(self, user, amount, currency):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM accounts WHERE email = %s and amount >= %s and currency = %s", (user, amount, currency,))
        myresult = mycursor.fetchall()
        return myresult

    def OnlineHistoryNumber(self):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT COUNT(*) FROM onlinehistory")
        res = mycursor.fetchone()
        number = res[0] + 1
        return number

    def AddOnlineTransactionHistory(self, sender, reciever, amount, currency):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        number = self.OnlineHistoryNumber()
        mycursor.execute("INSERT INTO onlinehistory (number, sender, reciever, amount, currency) VALUES(%s, %s, %s, %s, %s)", (number, sender, reciever, amount, currency,))
        database.commit()

    def RemoveMoneyFromAccount(self, sender, amount, currency):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT amount FROM accounts WHERE email = %s and currency = %s", (sender, currency,))
        res = mycursor.fetchone()
        balance = float(res[0]) - float(amount)
        mycursor.execute("UPDATE accounts SET amount = %s WHERE email = %s and currency = %s", (balance, sender, currency,))
        database.commit()

    def UserExistInCardsByEmail(self, user):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM cards WHERE email = %s", (user,))
        myresult = mycursor.fetchall()
        return myresult

    def UserExistInCardsByNumber(self, user):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM cards WHERE number = %s", (user,))
        myresult = mycursor.fetchall()
        return myresult

    def GetEmailFromUserByCardNumber(self, user):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT email FROM cards WHERE number = %s", (user,))
        res = mycursor.fetchone()
        return res[0]

    def AddNewAccountOnline(self, mail, currency, amount):
        number = self.AccountNumber()
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("INSERT INTO accounts (number, email, amount, currency) VALUES(%s, %s, %s, %s)", (number, mail, amount, currency,))
        database.commit()

    def UpdateAccountOnline(self, mail, currency, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        oldBalance = self.GetAccountBalance(mail, currency)
        newBalance = float(oldBalance) + amount
        mycursor.execute("UPDATE accounts SET amount = %s WHERE email = %s AND currency = %s", (newBalance, mail, currency,))
        database.commit()


    def MakeExchange(self, user, fromCurrency, toCurrency, amount):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        self.RemoveMoneyFromAccount(user, amount, fromCurrency)
        newBalance = CurrencyRates().convert(fromCurrency, toCurrency, float(amount))
        if not self.HasThatCurrency(user, toCurrency):
            self.AddNewAccountOnline(user, toCurrency, newBalance)
        else:
            self.UpdateAccountOnline(user, toCurrency, newBalance)

    def GetBankHistory(self, user):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM bankhistory WHERE sender = %s or reciever = %s", (user, user,))
        row_headers=[x[0] for x in mycursor.description]
        rv = mycursor.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
        value = json.dumps(json_data)
        return value

    def GetOnlineHistory(self, user):
        database = mysql.connector.connect(host="localhost", user="root", password = "1234", database="drs")
        mycursor = database.cursor()
        mycursor.execute("SELECT * FROM onlinehistory WHERE sender = %s or reciever = %s", (user, user,))
        row_headers=[x[0] for x in mycursor.description]
        rv = mycursor.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
        value = json.dumps(json_data)
        return value