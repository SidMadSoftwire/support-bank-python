import csv

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

def update_accounts(file, accounts):
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for account in accounts:
                payer = False
                payee = False
                if account.name == row['From']:
                    account.balance -= float(row['Amount'])
                    payer = True
                elif account.name == row['To']:
                    account.balance += float(row['Amount'])
                    payee = True

                if payer and payee:
                    break
            else:
                if not payer:
                    accounts.append(Account(row['From'], -(float(row['Amount']))))
                if not payee:
                    accounts.append(Account(row['To'], float(row['Amount'])))

def main():
    accounts = []
    transactions = 'Transactions2014.csv'
    update_accounts(transactions, accounts)

    command = ""
    while command != "Exit":
        command = input('Enter command: ')

        if command == 'List All':
            for account in accounts:
                print(f'Name: {account.name}, Balance: {account.balance}')
        elif command.startswith('List ') and len(command) >= 6:
            for account in accounts:
                if command[5:] == account.name:
                    with open(transactions, newline='') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            


        elif command == 'Exit':
            break
        else:
            print('Invalid command')
