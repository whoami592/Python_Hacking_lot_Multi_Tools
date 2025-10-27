import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import hashlib
import os
from datetime import datetime

class OmniBank:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OmniBank - Secure Banking System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Data file
        self.data_file = "omnibank_data.csv"
        self.init_database()
        
        # Current user session
        self.current_user = None
        
        # Style for professional look
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Heading.TLabel", font=("Arial", 12, "bold"))
        style.configure("TButton", font=("Arial", 10))
        
        self.show_login()
    
    def hash_password(self, password):
        """Secure password hashing using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def init_database(self):
        """Initialize CSV database if not exists"""
        if not os.path.exists(self.data_file):
            # Columns: id, username, hashed_password, account_number, balance, transactions (JSON-like string)
            df = pd.DataFrame(columns=["id", "username", "hashed_password", "account_number", "balance", "transactions"])
            df.to_csv(self.data_file, index=False)
    
    def load_data(self):
        """Load data from CSV"""
        return pd.read_csv(self.data_file)
    
    def save_data(self, df):
        """Save data to CSV"""
        df.to_csv(self.data_file, index=False)
    
    def validate_login(self, username, password):
        """Validate user credentials"""
        df = self.load_data()
        hashed_pw = self.hash_password(password)
        user_row = df[(df["username"] == username) & (df["hashed_password"] == hashed_pw)]
        return not user_row.empty, user_row.iloc[0]["account_number"] if not user_row.empty else None
    
    def create_account(self, username, password, initial_balance=0):
        """Create new user account"""
        df = self.load_data()
        if username in df["username"].values:
            return False, "Username already exists!"
        
        hashed_pw = self.hash_password(password)
        new_id = len(df) + 1
        account_num = f"ACC{new_id:04d}"
        new_row = pd.DataFrame({
            "id": [new_id],
            "username": [username],
            "hashed_password": [hashed_pw],
            "account_number": [account_num],
            "balance": [initial_balance],
            "transactions": [f"Account Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Balance: {initial_balance}"]
        })
        self.save_data(pd.concat([df, new_row], ignore_index=True))
        return True, account_num
    
    def get_balance(self, account_num):
        """Get account balance"""
        df = self.load_data()
        row = df[df["account_number"] == account_num]
        return row.iloc[0]["balance"] if not row.empty else 0
    
    def update_balance(self, account_num, new_balance, transaction_desc):
        """Update balance and append transaction"""
        df = self.load_data()
        row_idx = df[df["account_number"] == account_num].index[0]
        current_transactions = df.at[row_idx, "transactions"]
        new_transaction = f"; {transaction_desc}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Balance: {new_balance}"
        df.at[row_idx, "balance"] = new_balance
        df.at[row_idx, "transactions"] = current_transactions + new_transaction
        self.save_data(df)
    
    def deposit(self, account_num, amount):
        """Process deposit"""
        if amount <= 0:
            return False, "Amount must be positive!"
        current_balance = self.get_balance(account_num)
        new_balance = current_balance + amount
        self.update_balance(account_num, new_balance, f"Deposit +{amount}")
        return True, new_balance
    
    def withdraw(self, account_num, amount):
        """Process withdrawal"""
        if amount <= 0:
            return False, "Amount must be positive!"
        current_balance = self.get_balance(account_num)
        if amount > current_balance:
            return False, "Insufficient funds!"
        new_balance = current_balance - amount
        self.update_balance(account_num, new_balance, f"Withdrawal -{amount}")
        return True, new_balance
    
    def get_transactions(self, account_num):
        """Get transaction history"""
        df = self.load_data()
        row = df[df["account_number"] == account_num]
        return row.iloc[0]["transactions"].split("; ") if not row.empty else []
    
    def show_login(self):
        """Login Window"""
        self.clear_window()
        title = ttk.Label(self.root, text="OmniBank Login", style="Title.TLabel")
        title.pack(pady=20)
        
        ttk.Label(self.root, text="Username:").pack()
        self.username_entry = ttk.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)
        
        ttk.Label(self.root, text="Password:").pack()
        self.password_entry = ttk.Entry(self.root, show="*", width=30)
        self.password_entry.pack(pady=5)
        
        ttk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self.root, text="Create Account", command=self.show_create_account).pack()
    
    def show_create_account(self):
        """Create Account Window"""
        self.clear_window()
        title = ttk.Label(self.root, text="Create New Account", style="Title.TLabel")
        title.pack(pady=20)
        
        ttk.Label(self.root, text="Username:").pack()
        self.new_username_entry = ttk.Entry(self.root, width=30)
        self.new_username_entry.pack(pady=5)
        self.new_username_entry.focus()
        
        ttk.Label(self.root, text="Password:").pack()
        self.new_password_entry = ttk.Entry(self.root, show="*", width=30)
        self.new_password_entry.pack(pady=5)
        
        ttk.Label(self.root, text="Initial Balance:").pack()
        self.balance_entry = ttk.Entry(self.root, width=30)
        self.balance_entry.insert(0, "0")
        self.balance_entry.pack(pady=5)
        
        ttk.Button(self.root, text="Create", command=self.create_new_account).pack(pady=10)
        ttk.Button(self.root, text="Back to Login", command=self.show_login).pack()
    
    def create_new_account(self):
        """Handle account creation"""
        username = self.new_username_entry.get().strip()
        password = self.new_password_entry.get().strip()
        try:
            initial_balance = float(self.balance_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid balance amount!")
            return
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password required!")
            return
        
        success, msg = self.create_account(username, password, initial_balance)
        if success:
            messagebox.showinfo("Success", f"Account created! Number: {msg}")
            self.show_login()
        else:
            messagebox.showerror("Error", msg)
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password required!")
            return
        
        success, account_num = self.validate_login(username, password)
        if success:
            self.current_user = {"username": username, "account_num": account_num}
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials!")
    
    def show_dashboard(self):
        """Main Dashboard"""
        self.clear_window()
        title = ttk.Label(self.root, text=f"Welcome, {self.current_user['username']}!", style="Title.TLabel")
        title.pack(pady=10)
        
        # Balance Display
        balance = self.get_balance(self.current_user["account_num"])
        balance_label = ttk.Label(self.root, text=f"Current Balance: ${balance:.2f}", style="Heading.TLabel")
        balance_label.pack(pady=10)
        
        # Buttons Frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Deposit", command=self.show_deposit).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Withdraw", command=self.show_withdraw).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="View Transactions", command=self.show_transactions).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Logout", command=self.logout).pack(side="left", padx=10)
    
    def show_deposit(self):
        """Deposit Window"""
        self.clear_window()
        title = ttk.Label(self.root, text="Deposit Funds", style="Title.TLabel")
        title.pack(pady=20)
        
        ttk.Label(self.root, text="Amount:").pack()
        self.deposit_entry = ttk.Entry(self.root, width=30)
        self.deposit_entry.pack(pady=5)
        self.deposit_entry.focus()
        
        ttk.Button(self.root, text="Deposit", command=self.process_deposit).pack(pady=10)
        ttk.Button(self.root, text="Back", command=self.show_dashboard).pack()
    
    def process_deposit(self):
        """Handle deposit"""
        try:
            amount = float(self.deposit_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
            return
        
        success, new_balance = self.deposit(self.current_user["account_num"], amount)
        if success:
            messagebox.showinfo("Success", f"Deposited ${amount:.2f}. New Balance: ${new_balance:.2f}")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", new_balance)
    
    def show_withdraw(self):
        """Withdraw Window"""
        self.clear_window()
        title = ttk.Label(self.root, text="Withdraw Funds", style="Title.TLabel")
        title.pack(pady=20)
        
        ttk.Label(self.root, text="Amount:").pack()
        self.withdraw_entry = ttk.Entry(self.root, width=30)
        self.withdraw_entry.pack(pady=5)
        self.withdraw_entry.focus()
        
        ttk.Button(self.root, text="Withdraw", command=self.process_withdraw).pack(pady=10)
        ttk.Button(self.root, text="Back", command=self.show_dashboard).pack()
    
    def process_withdraw(self):
        """Handle withdrawal"""
        try:
            amount = float(self.withdraw_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
            return
        
        success, new_balance = self.withdraw(self.current_user["account_num"], amount)
        if success:
            messagebox.showinfo("Success", f"Withdrew ${amount:.2f}. New Balance: ${new_balance:.2f}")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", new_balance)
    
    def show_transactions(self):
        """Transaction History Window"""
        self.clear_window()
        title = ttk.Label(self.root, text="Transaction History", style="Title.TLabel")
        title.pack(pady=10)
        
        transactions = self.get_transactions(self.current_user["account_num"])
        
        # Scrollable Text for History
        text_frame = ttk.Frame(self.root)
        text_frame.pack(pady=10, fill="both", expand=True)
        
        text = tk.Text(text_frame, height=20, width=70, wrap="word")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for trans in transactions:
            text.insert("end", trans + "\n")
        
        text.config(state="disabled")
        
        ttk.Button(self.root, text="Back", command=self.show_dashboard).pack(pady=10)
    
    def logout(self):
        """Logout and return to login"""
        self.current_user = None
        self.show_login()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    # Create default admin if not exists
    app = OmniBank()
    df = app.load_data()
    if len(df) == 0:
        app.create_account("admin", "admin123", 1000)
    app.run()