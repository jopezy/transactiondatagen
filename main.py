import pandas as pd
import os
import random
import string
from datetime import datetime
from faker import Faker

fake = Faker()

# Define the target location for exports
target_location = "C:/paymentdatatesting"  # Change this to your desired directory

# Define the variables for test data
savings_account_percentage = 0  # 0%
current_account_percentage = 1.0  # 100%
# Define maximum accounts per customer
max_savings_accounts_per_customer = 2  # Up to 2 savings accounts per customer
max_current_accounts_per_customer = 3   # Up to 3 current accounts per customer

# Define the number of customers
no_of_customers = 100

# Define the number of transactions
no_of_transactions = 2000

# Data timeframe
data_starting_date = pd.to_datetime("2023-01-01")
data_end_date = pd.to_datetime("2023-09-30")

# Function to create a timestamped folder
def create_timestamped_folder(target_location):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Folder format yyyymmdd_hhmmss
    folder_name = os.path.join(target_location, f"export_{timestamp}")
    os.makedirs(folder_name, exist_ok=True)  # Create the folder
    return folder_name

# Function to export the DataFrame to CSV
def export_to_csv(df, folder_name, table_name):
    csv_path = os.path.join(folder_name, f"{table_name}.csv")  # Path within the timestamped folder
    df.to_csv(csv_path, index=False)
    print(f"Table '{table_name}' exported to '{csv_path}'.")

# Function to export tables
def export_tables(tables, target_location):
    folder_name = create_timestamped_folder(target_location)  # Create a timestamped folder
    for table_name, df in tables.items():
        export_to_csv(df, folder_name, table_name)  # Export each DataFrame to CSV

# Function to generate a random birthdate
def generate_birthdate():
    start_date = pd.to_datetime("2004-12-31")
    end_date = pd.to_datetime("1934-12-31")
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date

# Function to generate a customer ID
def generate_finnish_customer_id(birthdate, is_female):
    # Format the date as ddmmyy
    ddmmyy = birthdate.strftime("%d%m%y")
    
    # Generate the first two random digits
    random_digits = ''.join(random.choices(string.digits, k=2))
    
    # Generate the third digit based on gender
    third_digit = random.choice([0, 2, 4, 6, 8]) if is_female else random.choice([1, 3, 5, 7, 9])
    
    # Generate the last character as either a digit or an uppercase letter
    last_char = random.choice(string.digits + string.ascii_uppercase)
    
    # Combine parts to form the customer ID
    customer_id = f"{ddmmyy}-{random_digits}{third_digit}{last_char}"
    
    return customer_id

# Function to create random customers
def create_random_customers(num_customers):
    customers = []
    customer_columns = ["CustomerID", "CustomerNumber", "FirstName", "LastName"]  # Define customer columns directly
    
    for i in range(num_customers):
        # Randomly select gender and generate names using Faker
        is_female = random.choice([True, False])
        first_name = fake.first_name_female() if is_female else fake.first_name_male()
        last_name = fake.last_name()
        customer_birthdate = generate_birthdate()
        customer_number = generate_finnish_customer_id(customer_birthdate, is_female)
        
        customer = {col: None for col in customer_columns}  # Initialize customer dict
        customer['CustomerID'] = i + 1  # Assign a unique key
        customer['CustomerNumber'] = customer_number
        customer['FirstName'] = first_name
        customer['LastName'] = last_name
        
        customers.append(customer)
    
    return pd.DataFrame(customers)

# Create accounts for customers
def create_accounts_for_customers(customers_df, data_starting_date):
    accounts = []
    
    for i, row in customers_df.iterrows():
        # Create savings accounts based on the percentage
        if random.random() < savings_account_percentage:
            for _ in range(random.randint(1, max_savings_accounts_per_customer)):
                account = {
                    "AccountID": len(accounts) + 1,
                    "CustomerID": row['CustomerID'],
                    "AccountBalance": round(random.uniform(100, 10000), 2),
                    "LastUpdated": None  # Placeholder for the timestamp
                }
                accounts.append(account)

        # Always create current accounts
        for _ in range(random.randint(1, max_current_accounts_per_customer)):
            account = {
                "AccountID": len(accounts) + 1,
                "CustomerID": row['CustomerID'],
                "AccountBalance": round(random.uniform(100, 10000), 2),
                "LastUpdated": data_starting_date  # Placeholder for the timestamp
            }
            accounts.append(account)
    
    return pd.DataFrame(accounts)

# Update accounts based on transactions
def update_fact_account(transactions_df, accounts_df):
    # Create a list to store the new account entries
    new_entries = []

    # Loop through each transaction
    for _, transaction in transactions_df.iterrows():
        # Find the corresponding account balance
        account_balance = accounts_df.loc[accounts_df['AccountID'] == transaction['AccountID'], 'AccountBalance'].values[0]
        new_balance = account_balance + transaction['TransactionAmount']  # Update balance

        # Create a new entry
        new_entry = {
            "AccountID": transaction['AccountID'],
            "CustomerID": transaction['CustomerID'],
            "AccountBalance": new_balance,
            "LastUpdated": transaction['TransactionTimestamp']  # Use transaction timestamp
        }
        new_entries.append(new_entry)

    # Convert the list of new entries to a DataFrame
    new_entries_df = pd.DataFrame(new_entries)

    # Append the new entries to the existing accounts DataFrame
    updated_accounts_df = pd.concat([accounts_df, new_entries_df], ignore_index=True)

    return updated_accounts_df

# Generate transactions

def generate_payment_transactions(customers_df, accounts_df, num_transactions):
    transactions = []
    
    for i in range(num_transactions):
        customer = random.choice(customers_df['CustomerID'].values)  # Randomly select a customer
        account = random.choice(accounts_df[accounts_df['CustomerID'] == customer]['AccountID'].values)  # Select an account for that customer
        transaction_amount = round(random.uniform(-1, -500), 2)  # Random amount
        transaction_type = random.choice(["Payment"])  # Only "Payment" as per your requirement
        
        # Generate a random timestamp within the defined date range
        transaction_timestamp = data_starting_date + (data_end_date - data_starting_date) * random.random()

        transaction = {
            "CustomerID": customer,
            "AccountID": account,
            "TransactionAmount": transaction_amount,
            "TransactionType": transaction_type,
            "TransactionTimestamp": transaction_timestamp
        }
        transactions.append(transaction)

    # Convert to DataFrame
    transactions_df = pd.DataFrame(transactions)

    # Sort transactions by TransactionTimestamp
    transactions_df.sort_values(by='TransactionTimestamp', inplace=True)

    # Reset index and create TransactionID based on sorted order
    transactions_df.reset_index(drop=True, inplace=True)
    transactions_df['TransactionID'] = transactions_df.index + 1  # Assign keys starting from 1

    return transactions_df

# Create customers
customers_df = create_random_customers(no_of_customers)

# Create accounts for the generated customers
accounts_df = create_accounts_for_customers(customers_df,data_starting_date)

# Create transactions
transactions_df = generate_payment_transactions(customers_df, accounts_df, no_of_transactions)

# Update the FactAccount based on the transactions
accounts_df = update_fact_account(transactions_df, accounts_df)

# Create tables dictionary
tables = {
    "DimCustomer": customers_df,
    "FactAccount": accounts_df,
    "FactPaymentTransaction": transactions_df
}

# Run the export
export_tables(tables, target_location)
