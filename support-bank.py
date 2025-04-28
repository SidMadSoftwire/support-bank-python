import csv
import json
import os
import logging
from datetime import datetime

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

class Transaction:
    def __init__(self, date, from_acc, to_acc, amount, narrative):
        self.date = date
        self.from_acc = from_acc
        self.to_acc = to_acc
        self.amount = amount
        self.narrative = narrative

    def date(self, new_date):
        self.date = new_date

    def amount(self, new_amount):
        self.amount = new_amount

def main():
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

    pending_transactions = []
    processed_transactions = []
    errors = []
    accounts = []

    dir_files = os.listdir('.')
    clear_files(dir_files)

    print('Welcome to SupportBank.')
    print_filenames(dir_files)

    command = ''
    while command != 'exit':
        command = input('Enter command: ').lower()

        # Import given file
        if command.startswith('import file ') and len(command) >= 13:
            if open_file(command[12:], dir_files, pending_transactions, errors):
                update_accounts(pending_transactions, processed_transactions, accounts)

        # List all account balances
        elif command == 'list all':
            list_all(accounts)

        # List transactions that involve a specific account
        elif command.startswith('list ') and len(command) >= 6:
            list_transactions(processed_transactions, accounts, command[5:])

        # List transactions that contains errors
        elif command == 'errors':
            list_errors(errors)

        # List currently available files
        elif command == 'files':
            print_filenames(dir_files)

        elif command == 'exit':
            logging.info('Exiting...')
            break

        else:
            print('Invalid command. Try [Import File FILENAME], [List All], [List NAME] or [Errors].  Use [Exit] to exit.')

# Update account balance based on transactions, skipping all in errors
def update_accounts(pending_transactions, processed_transactions, accounts):
    logging.info('Updating accounts from current file')
    for idx, trans in enumerate(pending_transactions):
        # Check if To and From accounts exist and update
        payer, payee = False, False
        for account in accounts:
            if account.name == trans.from_acc and payer == False:
                account.balance -= trans.amount
                payer = True
            elif account.name == trans.to_acc and payee == False:
                account.balance += trans.amount
                payee = True

            if payer and payee:
                break

        # If either To or From accounts don't exist, create account for them
        else:
            if not payer:
                accounts.append(Account(trans.from_acc, -trans.amount))
            if not payee:
                accounts.append(Account(trans.to_acc, trans.amount))

        processed_transactions.append(trans)

    pending_transactions.clear()
    logging.info('Processed transactions.')
    print('Accounts updated with the given transactions.')


# List all account balances
def list_all(accounts):
    logging.info('Listing all accounts')
    if len(accounts) == 0:
        print('No accounts found')
    else:
        for account in accounts:
            print(f'Name: {account.name}, Balance: £{account.balance:0.2f}')

# List all transactions by a given account (if it exists), skipping any in errors
def list_transactions(transactions, accounts, name):
    logging.info('Listing transactions from given user')
    for account in accounts:
        if name == account.name.lower():
            for idx, trans in enumerate(transactions):
                if trans.from_acc == account.name:
                    print(
                        f'Date: {trans.date}, To: {trans.to_acc}, Amount: £-{trans.amount:0.2f}, {trans.narrative}')
                elif trans.to_acc == account.name:
                    print(
                        f'Date: {trans.date}, From: {trans.from_acc}, Amount: £{trans.amount:0.2f}, {trans.narrative}')
            break
    else:
        print('No account by that name. Check accounts with [List All].')

# Open given file and write it to transactions.
# If error, user can choose to skip (note line in errors) or cancel the whole file, which returns False
def open_file(user_file_no, dir_files, transactions, errors):
    try:
        file_no = int(user_file_no) - 1
    except ValueError:
        print("Please pick one of the listed files by number. Try the [Files] command.")
        return False
    if not 0 <= file_no < len(dir_files):
        print("Please pick one of the listed files by number. Try the [Files] command.")
        return False

    if dir_files[file_no][-3:] == 'csv':
        open_csv(dir_files[file_no], transactions, errors)
        return True
    elif dir_files[file_no][-4:] == 'json':
        open_json(dir_files[file_no], transactions, errors)
        return True
    else:
        print("Only CSV, JSON files are supported.")
        return False

def open_csv(file, transactions, errors):
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            command = ''
            try:
                date = datetime.strptime(row['Date'], '%d/%m/%Y')
            except ValueError:
                logging.error(f'Invalid date format: {row["Date"]}')
                command = user_error_prompt(idx, 'date should be DD/MM/YYYY')
            try:
                amount = float(row['Amount'])
            except ValueError:
                logging.error(f'Invalid amount format: {row["Amount"]}')
                command = user_error_prompt(idx, 'amount is not numeric')

            if command == 'cancel':
                transactions.clear()
                errors.clear()
                logging.info('Cancelled opening CSV file.')
                return
            elif command == 'skip':
                errors.append(Transaction(date.strftime('%a %d %b %Y'), row['From'], row['To'], amount, row['Narrative']))
            else:
                transactions.append(Transaction(date.strftime('%a %d %b %Y'), row['From'], row['To'], amount, row['Narrative']))

    logging.info('Successfully opened CSV file.')

def open_json(file, transactions, errors):
    with open(file, 'r') as jsonfile:
        data = json.load(jsonfile)

        for idx, row in enumerate(data):
            command = ''
            try:
                date = datetime.strptime(row['Date'][:10], '%Y-%m-%d')
            except ValueError:
                logging.error(f'Invalid date format: {row['Date']}')
                command = user_error_prompt(idx, 'date should start YYYY-MM-DD')
            try:
                amount = float(row['Amount'])
            except ValueError:
                logging.error(f'Invalid amount format: {row['Amount']}')
                command = user_error_prompt(idx, 'amount is not numeric')

            if command == 'cancel':
                transactions.clear()
                errors.clear()
                logging.info('Cancelled opening JSON file.')
                return
            elif command == 'skip':
                errors.append(Transaction(date.strftime('%a %d %b %Y'), row['FromAccount'], row['ToAccount'], amount, row['Narrative']))
            else:
                transactions.append(Transaction(date.strftime('%a %d %b %Y'), row['FromAccount'], row['ToAccount'], amount, row['Narrative']))

        logging.info('Successfully opened JSON file.')


def user_error_prompt(idx, error):
    print(f'The transaction at line {idx} includes the following: {error}')
    print('Would you like to [skip] this line and continue reading the file?')
    print('Or would you rather [cancel] reading the file entirely?')
    command = ''
    while command not in ['skip', 'cancel']:
        command = input('Choice: ').lower()
        if command == 'skip':
            return command
        elif command == 'cancel':
            return command
        else:
            print('Invalid command. Would you like to [skip] or [cancel]?')
    return command


# List all transactions with errors
def list_errors(errors):
    if len(errors) == 0:
        print('No errors found.')
    else:
        for trans in errors:
            print(f'Date: {trans.date}, From: {trans.from_acc}, To: {trans.to_acc}, Amount: £{trans.amount}, {trans.narrative}')

def print_filenames(dir_files):
    print('Available files:')
    for idx, file in enumerate(dir_files):
        print(f'{idx + 1} - {file}')

def clear_files(dir_files):
    dir_files.remove('SupportBank.log')
    dir_files.remove('.git')
    dir_files.remove('.idea')
    dir_files.remove('pyproject.toml')
    dir_files.remove('poetry.lock')
    dir_files.remove('support-bank.py')

main()