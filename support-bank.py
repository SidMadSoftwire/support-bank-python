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
    errors = []
    #file = 'Transactions2014.csv'
    file = 'DodgyTransactions2015.csv'
    if not open_file(file, transactions, errors):
        transactions, errors = [], []

    #Calculate account balance
    accounts = []
    update_accounts(transactions, errors, accounts)

    command = ""
    while command != "exit":
        command = input('Enter command: ').lower()

        # List all account balances
        if command == 'list all':
            list_all(accounts)

        # List transactions that involve a specific account
        elif command.startswith('list ') and len(command) >= 6:
            list_transactions(transactions, errors, accounts, command[5:])

        # List transactions that contains errors
        elif command == 'errors':
            list_errors(transactions, errors)

        elif command == 'exit':
            logging.info('Exiting...')
            break

        else:
            print('Invalid command. Try [List All], [List NAME] or [Errors].  Use [Exit] to exit.')

# Update account balance based on transactions, skipping all in errors
def update_accounts(transactions, errors, accounts):
    logging.info('Updating accounts from current file')
    for idx, row in enumerate(transactions):
        if idx not in errors:
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

# List all account balances
def list_all(accounts):
    logging.info('Listing all accounts')
    if len(accounts) == 0:
        print("No accounts found")
    else:
        for account in accounts:
            print(f'Name: {account.name}, Balance: £{account.balance:0.2f}')

# List all transactions by a given account (if it exists), skipping any in errors
def list_transactions(transactions, errors, accounts, name):
    logging.info('Listing transactions from %s', name)
    for account in accounts:
        if name == account.name.lower():
            for idx, row in enumerate(transactions):
                if idx not in errors:
                    if row['From'] == account.name:
                        print(
                            f'Date: {row["Date"]}, To: {row["To"]}, Amount: £-{float(row["Amount"]):0.2f}, {row["Narrative"]}')
                    elif row['To'] == account.name:
                        print(
                            f'Date: {row["Date"]}, From: {row["From"]}, Amount: £{float(row["Amount"]):0.2f}, {row["Narrative"]}')
            break
    else:
        print('No account by that name. Check accounts with "List All".')

# Open given file and write it to transactions.
# If error, user can choose to skip (note line in errors) or cancel the whole file, which returns False
def open_file(file, transactions, errors):
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                datetime.strptime(row['Date'], '%d/%m/%Y')
                float(row['Amount'])
            except ValueError:
                print("The following transaction include data in the wrong format :")
                print(row)
                print("Would you like to [skip] this line and continue reading the file?")
                print("Or would you rather [cancel] reading the file entirely?")
                command = ''
                while command not in ['skip', 'cancel']:
                    command = input('What do?: ').lower()
                    if command == 'skip':
                        errors.append(len(transactions))
                        transactions.append(row)
                    elif command == 'cancel':
                        return False
                    else:
                        print('Invalid command. Would you like to [skip] or [cancel]?')
            else:
                transactions.append(row)
    return True

# List all transactions with errors
def list_errors(transactions, errors):
    for idx, row in enumerate(transactions):
        if idx in errors:
            print(
                f'Date: {row["Date"]}, From: {row["From"]}, Amount: £{row["Amount"]}, {row["Narrative"]}')


main()