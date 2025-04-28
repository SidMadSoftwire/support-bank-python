import csv
import logging
import re

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

def main():
    logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG)

    transactions = []
    errors = []
    accounts = []

    command = ''
    while command != 'exit':
        command = input('Enter command: ').lower()

        # Import given file
        if command.startswith('import file ') and len(command) >= 13:
            open_file(command[12:], transactions, errors)
            update_accounts(transactions, errors, accounts)

        # List all account balances
        elif command == 'list all':
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
            print('Invalid command. Try [Import File FILENAME], [List All], [List NAME] or [Errors].  Use [Exit] to exit.')

# Update account balance based on transactions, skipping all in errors
def update_accounts(transactions, errors, accounts):
    logging.info('Updating accounts from current file')
    for idx, row in enumerate(transactions):
        if idx not in errors:
            payer, payee = False, False
            for account in accounts:
                if account.name == row['From'] and payer == False:
                    account.balance -= float(row['Amount'])
                    payer = True
                elif account.name == row['To'] and payee == False:
                    account.balance += float(row['Amount'])
                    payee = True

                if payer and payee:
                    break
            else:
                if not payer:
                    accounts.append(Account(row['From'], -(float(row['Amount']))))
                if not payee:
                    accounts.append(Account(row['To'], float(row['Amount'])))

# List all account balances
def list_all(accounts):
    logging.info('Listing all accounts')
    if len(accounts) == 0:
        print('No accounts found')
    else:
        for account in accounts:
            print(f'Name: {account.name}, Balance: £{account.balance:0.2f}')

# List all transactions by a given account (if it exists), skipping any in errors
def list_transactions(transactions, errors, accounts, name):
    logging.info('Listing transactions from given user')
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
        print('No account by that name. Check accounts with [List All].')

# Open given file and write it to transactions.
# If error, user can choose to skip (note line in errors) or cancel the whole file, which returns False
def open_file(file, transactions, errors):
    if file[-3:] == 'csv':
        open_csv(file, transactions, errors)
    elif file[-4:] == 'json':
        open_json(file, transactions, errors)
    else:
        print("Only CSV, JSON files are supported.")

def open_csv(file, transactions, errors):
    try:
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader):
                command = ''
                if not re.fullmatch('[0-9]{2}/[0-9]{2}/[0-9]{4}', row['Date']):
                    logging.error(f'Invalid date format: {row["Date"]}')
                    command = user_error_prompt(idx, "date not formatted as DD/MM/YYYY")
                try:
                    float(row['Amount'])
                except ValueError:
                    logging.error(f'Invalid amount format: {row["Amount"]}')
                    command = user_error_prompt(idx, "amount is not numeric")

                if command == 'cancel':
                    transactions.clear()
                    errors.clear()
                    return False
                elif command == 'skip':
                    errors.append(idx)
                    transactions.append(row)
                else:
                    transactions.append(row)
    except OSError:
        logging.error('File not found')
    return True

def open_json(file, transactions, errors):
    # TODO
    print('')


def user_error_prompt(idx, error):
    print(f'The transaction at line {idx} includes the following: {error}')
    print('Would you like to [skip] this line and continue reading the file?')
    print('Or would you rather [cancel] reading the file entirely?')
    command = ''
    while command not in ['skip', 'cancel']:
        command = input('Choice: ').lower()
        if command == 'skip':
            return 'skip'
        elif command == 'cancel':
            return 'cancel'
        else:
            print('Invalid command. Would you like to [skip] or [cancel]?')


# List all transactions with errors
def list_errors(transactions, errors):
    for idx, row in enumerate(transactions):
        if idx in errors:
            print(
                f'Date: {row["Date"]}, From: {row["From"]}, Amount: £{row["Amount"]}, {row["Narrative"]}')


main()