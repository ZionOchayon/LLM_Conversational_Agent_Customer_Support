import shelve
import random
import os

# Define the possible statuses
statuses = ['Shipped', 'Pending', 'Delivered', 'Processing']

# Define the path to the databases folder
db_folder = 'databases'

# Initialize the database
def initialize_database(db_name):
    db_path = os.path.join(db_folder, db_name)
    with shelve.open(db_path) as db:
        for order_id in range(100, 201):
            db[str(order_id)] = random.choice(statuses)

# Verify the data
def verify_database(db_name):
    db_path = os.path.join(db_folder, db_name)
    with shelve.open(db_path) as db:
        for order_id in range(100, 201):
            print(f'Order ID: {order_id}, Status: {db[str(order_id)]}')

# ----- Please do not run due to testing based on existing orders. -----

# Usage:
# initialize_database('orders_db')
verify_database('orders_db')
