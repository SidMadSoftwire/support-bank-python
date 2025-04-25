import csv
import logging
from datetime import datetime

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

def main():
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

    #Read file to dictionary while checking validity
    transactions = []
    file = 'Transactions2014.csv'
    #transactions = 'DodgyTransactions2015.csv'
    open_file(file, transactions)

    #Calculate account balance
    accounts = []
    update_accounts(transactions, accounts)

    command = ""
    while command != "exit":
        command = input('Enter command: ').lower()

        # List all account balances
        if command == 'list all':
            list_all(accounts)

        # List transactions that involve a specific account
        elif command.startswith('list ') and len(command) >= 6:
            list_transactions(transactions, accounts, command[5:])

        elif command == 'exit':
            logging.info('Exiting...')
            break
        else:
            print('Invalid command. Try "List All" or "List [name]". Use "Exit" to exit.')

def update_accounts(transactions, accounts):
    logging.info('Updating accounts from current file')
    for row in transactions:
        logging.info('New transaction at %s from %s to %s', row['Date'], row['From'], row['To'])
        payer, payee = False, False
        for account in accounts:
            if account.name == row['From'] and payer == False:
                logging.info('Taking %s from balance', row['Amount'])
                account.balance -= float(row['Amount'])
                payer = True
            elif account.name == row['To'] and payee == False:
                logging.info('Adding %s to balance', row['Amount'])
                account.balance += float(row['Amount'])
                payee = True

            if payer and payee:
                break
        else:
            if not payer:
                logging.info('Creating account with balance -%s', row['Amount'])
                accounts.append(Account(row['From'], -(float(row['Amount']))))
            if not payee:
                logging.info('Creating account with balance %s', row['Amount'])
                accounts.append(Account(row['To'], float(row['Amount'])))

def list_all(accounts):
    logging.info('Listing all accounts')
    for account in accounts:
        print(f'Name: {account.name}, Balance: £{account.balance:0.2f}')

def list_transactions(transactions, accounts, name):
    logging.info('Listing transactions from %s', name)
    for account in accounts:
        if name == account.name.lower():
            for row in transactions:
                if row['From'] == account.name:
                    print(
                        f'Date: {row["Date"]}, To: {row["To"]}, Amount: £-{float(row["Amount"]):0.2f}, {row["Narrative"]}')
                elif row['To'] == account.name:
                    print(
                        f'Date: {row["Date"]}, From: {row["From"]}, Amount: £{float(row["Amount"]):0.2f}, {row["Narrative"]}')
            break
    else:
        print('No account by that name. Check accounts with "List ALl".')

def open_file(file, transactions):
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                datetime.strptime(row['Date'], '%d/%m/%Y')
                float(row['Amount'])
            except ValueError:
                print("Oh no!")
                break
                # TODO
            else:
                transactions.append(row)



main()