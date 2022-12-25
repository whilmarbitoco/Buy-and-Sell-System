import sqlite3
import sys


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def sale(item, price, quantity):
    global username

    cursor.execute("INSERT INTO items (item, price, quantity, seller) VALUES (?, ?, ?, ?)", (item, price, quantity, username))
    print(f"""
    PRODUCTS ADDED
    Item: {item}
    Price: {price}
    Quantity: {quantity}
    Seller: {username}
    """)
    conn.commit()


def display():
  cursor.execute("SELECT * FROM items")
  rows = cursor.fetchall()
  for row in rows:
      item = row[1]
      price = row[2]
      quantity = row[3]
      seller = row[4]
      if quantity == 0:
          cursor.execute("DELETE FROM items WHERE quantity=?", (quantity,))
      else:
          print(f"""
  +------------+
  |    Item    | {item}   
  +------------+
  |    Price   | {price}  
  +------------+
  |  Quantity  | {quantity} 
  +------------+
  |   Seller   | {seller} 
  +------------+
    """)



def check(item, quantity):
    cursor.execute("SELECT item, price, quantity FROM items WHERE item=?", (item,))
    row = cursor.fetchone()
    if row is not None:
        item_name, item_price, item_quantity = row
        if int(item_quantity) < int(quantity):
            print("Not enough items in stock")
            return False
        total = int(item_price) * int(quantity)
        print(f""" 
        Item: {item_name}
        Quantity: {quantity}
        Total: {total}
        """)
        return True
    else:
        print(f"Item {item} not found")
        return False

def buy(name, quantity):
    global username

    if not check(name, quantity):
        return

    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    balance = cursor.fetchone()[0]

    cursor.execute("SELECT quantity, price, seller FROM items WHERE item=?", (name,))
    row = cursor.fetchone()
    if row is None:
        print(f"Item {name} not found")
        return
    item_quantity, item_price, seller = row
    newquan = int(item_quantity) - int(quantity)

    if balance is None:
        print("Insufficient funds")
        return

    elif int(balance) < int(item_price):
        print("Insufficient funds")
        return

    purchase_total = int(item_price) * int(quantity)
    new_balance = int(balance) - purchase_total
    cursor.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))

    cursor.execute("SELECT balance FROM users WHERE username = ?", (seller,))
    selbal = cursor.fetchone()[0]
    
    if selbal is not None:
      newselbal = int(selbal) + purchase_total
      cursor.execute("UPDATE users SET balance=? WHERE username=?", (newselbal, seller))
  
      cursor.execute("UPDATE items SET quantity=? WHERE item=?", (newquan, name))
      conn.commit()
      log(name, item_price, quantity)
    print("Transaction successful")
    print(f"Remaining Balance: {getbal()}")

    


def addbal(balance):
    global username
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    curbal = cursor.fetchone()[0]

    if curbal is None:
        newbal = balance
    else:
        newbal = int(curbal) + int(balance)

    cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (newbal, username))
    print(f"Balance Updated: {newbal}")
    conn.commit()




def getbal():
    global username
    cursor.execute("SELECT balance FROM users WHERE username = ?", (username,))
    balance = cursor.fetchone()[0]
    return balance



def log(item, price, quantity):
    global username
    cursor.execute("INSERT INTO transactions(username, item, price, quantity) VALUES (?, ?, ?, ?)", (username, item, price, quantity))
    conn.commit()



def getlog():
    global username
    cursor.execute("SELECT * FROM transactions WHERE username = ?", (username,))
    rows = cursor.fetchall()
    x = 0
    for row in rows:
        x += 1
        username = row[0]
        item = row[1]
        price = row[2]
        quantity = row[3]
        print(f"[{x}] Purchased of {username}")
        print(f"""
  +------------+
  |    Item    | {item}   
  +------------+
  |    Price   | {price}  
  +------------+
  |  Quantity  | {quantity} 
  +------------+
        """)



def main():
  menu = """ 
  [1] Buy
  [2] Sell
  [3] Store
  [4] Balance
  [5] Transactions
  [6] Exit
  """
  
  print(menu)
  customer = input("[Choose]►  ")
  
  if customer == "1":
    display()
    item = input("Item Name: ")
    quantity = input("Item Quantity: ")
    if check(item, quantity):
      print(""" 
  [1] Buy
  [2] Cancel
      """)
      purchase = input("[Confirm]►  ")
      if purchase == "1":
        buy(item, quantity)
      elif purchase == "2":
        print("Transaction Cancelled")
      else:
        print("Please choose between 1 and 2")
  elif customer == "2":
    item = input("Item Name: ")
    price = input("Item Price: ")
    quantity = input("Item Quantity: ")
    sale(item, price, quantity)
  
  elif customer == "3":
    display()
  
  elif customer == "4":
    print("""
  [1] Check balance
  [2] Add Balance
    """)
    prompt = input("[Balance]► ")
    if prompt == "1":
      print(f"Current Balance: {getbal()}")
    elif prompt == "2":
      val = input("Deposit: ")
      addbal(val)
    else:
      print("Please choose between 1 and 2")
    
  elif customer == "5":
    getlog()

  elif customer == "6":
    sys.exit()
    
  else:
    print("Please choose between 1, 2 and 3")
    


def login(username, password):
    cursor.execute('''
    SELECT * FROM users
    WHERE username=? AND password=?
    ''', (username, password))
    user = cursor.fetchone()
    if user is not None:
        return True
    else:
        print("User does not exist")
        return False



def signup(username, password):
    cursor.execute('''
    INSERT INTO users (username, password)
    VALUES (?, ?)
    ''', (username, password))
    print("Account Created")
    conn.commit()



username = None
while True:
  menu =""" 
  [1] Login
  [2] Sign Up
  [3] Exit
  """
  print(menu)
  prompt = input("[Choose]► ")
  
  if prompt == "1":
    username = input("username: ")
    password = input("password: ")
    if login(username, password):
      print("\n")
      print(f"Welcome, {username}!")
      print(f"Uncrown Kings Market")
      while login(username, password):
        main()
    else:
      pass
  
  elif prompt == "2":
    username = input("username: ")
    password = input("password: ")
    signup(username, password)
  
  elif prompt == "3":
    sys.exit()
    
  else:
    print("Please choose between 1 and 2")
