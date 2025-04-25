import csv
import logging

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

def update_accounts(file, accounts):
    with open(file, newline='') as csvfile:
        logging.debug('Updating accounts from %s', file)
        reader = csv.DictReader(csvfile)
        for row in reader:
            logging.debug('New transaction at %s from %s to %s', row['Date'], row['From'], row['To'])
            payer, payee = False, False
            for account in accounts:
                if account.name == row['From'] and payer == False:
                    logging.debug('Taking %s from balance', row['Amount'])
                    account.balance -= float(row['Amount'])
                    payer = True
                elif account.name == row['To'] and payee == False:
                    logging.debug('Adding %s to balance', row['Amount'])
                    account.balance += float(row['Amount'])
                    payee = True

                if payer and payee:
                    break
            else:
                if not payer:
                    logging.debug('Creating account with balance -%s', row['Amount'])
                    accounts.append(Account(row['From'], -(float(row['Amount']))))
                if not payee:
                    logging.debug('Creating account with balance %s', row['Amount'])
                    accounts.append(Account(row['To'], float(row['Amount'])))

def list_all(accounts):
    logging.debug('Listing all accounts')
    for account in accounts:
        print(f'Name: {account.name}, Balance: £{account.balance:0.2f}')

def list_transactions(transactions, accounts, name):
    logging.debug('Listing transactions from %s', name)
    for account in accounts:
        if name == account.name:
            with open(transactions, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['From'] == account.name:
                        logging.debug('Transaction -%s', row['Amount'])
                        print(
                            f'Date: {row["Date"]}, To: {row["To"]}, Amount: £-{float(row["Amount"]):0.2f}, {row["Narrative"]}')
                    elif row['To'] == account.name:
                        logging.debug('Transaction %s', row['Amount'])
                        print(
                            f'Date: {row["Date"]}, From: {row["From"]}, Amount: £{float(row["Amount"]):0.2f}, {row["Narrative"]}')
            break
    else:
        print('No account by that name.')

def main():
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

    accounts = []
    transactions = 'Transactions2014.csv'
    #transactions = 'DodgyTransactions2015.csv'
    update_accounts(transactions, accounts)

    command = ""
    while command != "Exit":
        command = input('Enter command: ')

        # List all account balances
        if command == 'List All':
            list_all(accounts)

        # List transactions that involve a specific account
        elif command.startswith('List ') and len(command) >= 6:
            list_transactions(transactions, accounts, command[5:])

        elif command == 'Exit':
            logging.debug('Exiting...')
            break
        else:
            print('Invalid command')

main()