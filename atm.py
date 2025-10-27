# ATM Machine Complete GUI with Advanced Graphic Design
# Coded by Mr Sabaz Ali Khan
# Date: September 15, 2025
# Features: PIN-based login, Balance check, Withdraw, Deposit, Transfer
# Database: CSV file for accounts (account_number, pin, balance)
# GUI: Tkinter with advanced styling, colors, fonts, and canvas for graphics

import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# Database file
DB_FILE = 'atm_accounts.csv'

# Sample data initialization
def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['account_number', 'pin', 'balance'])
            # Sample accounts
            writer.writerow(['123456', '1234', 1000.00])
            writer.writerow(['789101', '5678', 2500.00])

# Load accounts into dict for quick access {account: {'pin': , 'balance': }}
def load_accounts():
    accounts = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                accounts[row['account_number']] = {
                    'pin': row['pin'],
                    'balance': float(row['balance'])
                }
    return accounts

# Save accounts back to CSV
def save_accounts(accounts):
    with open(DB_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['account_number', 'pin', 'balance'])
        for acc_num, data in accounts.items():
            writer.writerow([acc_num, data['pin'], data['balance']])

# Main ATM Class
class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Machine - Advanced GUI")
        self.root.geometry("800x600")
        self.root.configure(bg='#0a0a0a')  # Dark background for advanced look
        
        # Load accounts
        self.accounts = load_accounts()
        self.current_account = None
        
        # Style configuration for advanced graphics
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), foreground='#00ff00', background='#0a0a0a')
        style.configure('Header.TLabel', font=('Arial', 18, 'bold'), foreground='#ffffff', background='#0a0a0a')
        style.configure('Info.TLabel', font=('Arial', 12), foreground='#cccccc', background='#0a0a0a')
        style.configure('Custom.TButton', font=('Arial', 14, 'bold'), foreground='#ffffff', background='#ff4500')
        style.map('Custom.TButton', background=[('active', '#ff6347')])
        
        # Canvas for advanced graphics (e.g., logo or border)
        self.canvas = tk.Canvas(root, width=800, height=100, bg='#0a0a0a', highlightthickness=0)
        self.canvas.pack()
        self.draw_graphics()
        
        # Initial screen: PIN Entry
        self.show_pin_screen()
    
    def draw_graphics(self):
        # Advanced graphic: Gradient-like lines and ATM logo
        self.canvas.create_rectangle(0, 0, 800, 100, fill='#1a1a1a', outline='#00ff00', width=2)
        self.canvas.create_text(400, 50, text="?? ATM MACHINE", font=('Arial', 28, 'bold'), fill='#00ff00')
        # Decorative lines
        for i in range(0, 800, 20):
            self.canvas.create_line(i, 0, i, 100, fill='#333333', width=1)
    
    def show_pin_screen(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()
        
        # Title
        title = ttk.Label(self.root, text="Enter Your PIN", style='Title.TLabel')
        title.pack(pady=20)
        
        # PIN Entry
        self.pin_var = tk.StringVar()
        pin_entry = ttk.Entry(self.root, textvariable=self.pin_var, show='*', font=('Arial', 16), width=10, justify='center')
        pin_entry.pack(pady=10)
        pin_entry.focus()
        
        # Account Number Label (assuming fixed for demo, or add entry)
        acc_label = ttk.Label(self.root, text="Account: 123456", style='Header.TLabel')
        acc_label.pack(pady=5)
        self.current_account = '123456'  # Demo fixed account
        
        # Login Button
        login_btn = ttk.Button(self.root, text="Login", style='Custom.TButton', command=self.login)
        login_btn.pack(pady=20)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
    
    def login(self):
        pin = self.pin_var.get()
        if self.current_account in self.accounts and self.accounts[self.current_account]['pin'] == pin:
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Invalid PIN!")
            self.pin_var.set("")
    
    def show_main_menu(self):
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()
        
        # Header
        header = ttk.Label(self.root, text=f"Welcome, Account {self.current_account}", style='Header.TLabel')
        header.pack(pady=20)
        
        # Buttons for menu
        btn_frame = tk.Frame(self.root, bg='#0a0a0a')
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Check Balance", style='Custom.TButton', command=self.show_balance).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="Withdraw", style='Custom.TButton', command=self.show_withdraw).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="Deposit", style='Custom.TButton', command=self.show_deposit).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(btn_frame, text="Transfer", style='Custom.TButton', command=self.show_transfer).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(btn_frame, text="Exit", style='Custom.TButton', command=self.exit_app).grid(row=2, column=0, columnspan=2, pady=20)
    
    def show_balance(self):
        balance = self.accounts[self.current_account]['balance']
        messagebox.showinfo("Balance", f"Your current balance is: ${balance:.2f}")
        self.show_main_menu()
    
    def show_withdraw(self):
        self.show_transaction_screen("Withdraw", self.withdraw)
    
    def withdraw(self, amount):
        balance = self.accounts[self.current_account]['balance']
        if amount > balance:
            messagebox.showerror("Error", "Insufficient funds!")
            return
        self.accounts[self.current_account]['balance'] -= amount
        save_accounts(self.accounts)
        messagebox.showinfo("Success", f"Withdrew ${amount:.2f}\nNew balance: ${self.accounts[self.current_account]['balance']:.2f}")
        self.show_main_menu()
    
    def show_deposit(self):
        self.show_transaction_screen("Deposit", self.deposit)
    
    def deposit(self, amount):
        self.accounts[self.current_account]['balance'] += amount
        save_accounts(self.accounts)
        messagebox.showinfo("Success", f"Deposited ${amount:.2f}\nNew balance: ${self.accounts[self.current_account]['balance']:.2f}")
        self.show_main_menu()
    
    def show_transfer(self):
        # Simple transfer to another account (demo)
        self.show_transaction_screen("Transfer", self.transfer, with_account=True)
    
    def transfer(self, amount, target_account):
        if target_account not in self.accounts:
            messagebox.showerror("Error", "Target account not found!")
            return
        balance = self.accounts[self.current_account]['balance']
        if amount > balance:
            messagebox.showerror("Error", "Insufficient funds!")
            return
        self.accounts[self.current_account]['balance'] -= amount
        self.accounts[target_account]['balance'] += amount
        save_accounts(self.accounts)
        messagebox.showinfo("Success", f"Transferred ${amount:.2f} to {target_account}\nNew balance: ${self.accounts[self.current_account]['balance']:.2f}")
        self.show_main_menu()
    
    def show_transaction_screen(self, title, action, with_account=False):
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()
        
        header = ttk.Label(self.root, text=title, style='Title.TLabel')
        header.pack(pady=20)
        
        # Amount entry
        amount_var = tk.StringVar()
        ttk.Label(self.root, text="Enter Amount ($):", style='Header.TLabel').pack(pady=5)
        amount_entry = ttk.Entry(self.root, textvariable=amount_var, font=('Arial', 16), width=15)
        amount_entry.pack(pady=10)
        amount_entry.focus()
        
        # Target account if transfer
        target_var = None
        if with_account:
            ttk.Label(self.root, text="Target Account:", style='Header.TLabel').pack(pady=5)
            target_var = tk.StringVar()
            target_entry = ttk.Entry(self.root, textvariable=target_var, font=('Arial', 16), width=15)
            target_entry.pack(pady=5)
        
        def process():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    raise ValueError
                if with_account:
                    target = target_var.get().strip()
                    if not target:
                        raise ValueError("Target account required")
                    action(amount, target)
                else:
                    action(amount)
            except ValueError:
                messagebox.showerror("Error", "Invalid amount or account!")
        
        ttk.Button(self.root, text="Confirm", style='Custom.TButton', command=process).pack(pady=20)
        ttk.Button(self.root, text="Back", style='Custom.TButton', command=self.show_main_menu).pack(pady=5)
        
        self.root.bind('<Return>', lambda e: process())
    
    def exit_app(self):
        save_accounts(self.accounts)
        self.root.quit()

# Initialize DB and run app
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ATMApp(root)
    root.mainloop()