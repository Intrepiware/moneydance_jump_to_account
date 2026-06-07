import sys
from javax.swing import JFrame, JTextField, JList, JScrollPane, DefaultListModel
from java.awt import BorderLayout
from java.awt.event import KeyAdapter, KeyEvent
from com.infinitekind.moneydance.model import AccountUtil

class QuickAccountSwitcher(object):
    def __init__(self, context, current_book):
        self.context = context
        self.book = current_book
        
        # 1. Fetch and store all accounts with their full path hierarchies
        self.all_accounts = []
        for acct in AccountUtil.getAccountIterator(self.book):
            # Exclude the root account itself
            if acct.getParentAccount():
                self.all_accounts.append(acct)
        
        # Sort accounts alphabetically by their full display name
        self.all_accounts.sort(key=lambda x: x.getFullAccountName().lower())
        
        # 2. Build the Swing UI components
        self.frame = JFrame("Jump to Account")
        self.frame.setSize(400, 300)
        self.frame.setLocationRelativeTo(None) # Center on screen
        self.frame.setLayout(BorderLayout())
        
        self.search_field = JTextField()
        self.list_model = DefaultListModel()
        self.account_list_ui = JList(self.list_model)
        
        # Populate the initial list with all accounts
        self.current_matches = list(self.all_accounts)
        self.update_list_view()
        
        # Add components to the frame
        self.frame.add(self.search_field, BorderLayout.NORTH)
        self.frame.add(JScrollPane(self.account_list_ui), BorderLayout.CENTER)
        
        # 3. Attach keyboard listeners for fluid, mouseless navigation
        self.search_field.addKeyListener(type('KeyAdapter', (KeyAdapter,), {
            'keyReleased': self.handle_key_released
        })())
        
        self.frame.setVisible(True)
        self.search_field.requestFocusInWindow()

    def update_list_view(self):
        self.list_model.clear()
        for acct in self.current_matches:
            self.list_model.addElement(acct.getFullAccountName())
        if self.current_matches:
            self.account_list_ui.setSelectedIndex(0)

    def handle_key_released(self, event):
        code = event.getKeyCode()
        
        # Arrow down moves focus from search field straight into the results list
        if code == KeyEvent.VK_DOWN:
            idx = self.account_list_ui.getSelectedIndex()
            if idx < self.list_model.getSize() - 1:
                self.account_list_ui.setSelectedIndex(idx + 1)
                self.account_list_ui.ensureIndexIsVisible(idx + 1)
                
        elif code == KeyEvent.VK_UP:
            idx = self.account_list_ui.getSelectedIndex()
            if idx > 0:
                self.account_list_ui.setSelectedIndex(idx - 1)
                self.account_list_ui.ensureIndexIsVisible(idx - 1)
                
        # Enter executes the jump
        elif code == KeyEvent.VK_ENTER:
            idx = self.account_list_ui.getSelectedIndex()
            if idx >= 0:
                target_account = self.current_matches[idx]
                uuid = target_account.getUUID()
                # Command Moneydance to jump to the selected account register
                self.context.showURL("moneydance:showaccount:uuid=" + uuid)
                self.frame.dispose() # Close switcher window
                
        # Escape closes the window
        elif code == KeyEvent.VK_ESCAPE:
            self.frame.dispose()
            
        # Any other key filters the list dynamically
        else:
            search_text = self.search_field.getText().lower()
            self.current_matches = [
                acct for acct in self.all_accounts 
                if search_text in acct.getFullAccountName().lower()
            ]
            self.update_list_view()

# Execution entry point inside Moneybot
try:
    # 'moneydance' and 'moneydance_data' are globally injected handles in the console
    book = moneydance_data
    # In older versions, use: book = moneydance.getCurrentAccountBook()
    
    # Initialize the UI switcher instance
    QuickAccountSwitcher(moneydance, book)
except NameError:
    print "Error: This script must be executed inside the Moneydance Moneybot Console."