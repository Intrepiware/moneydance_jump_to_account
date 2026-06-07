import sys
from javax.swing import JDialog, JTextField, JList, JScrollPane, DefaultListModel, SwingUtilities, WindowConstants, BorderFactory
from java.awt import BorderLayout, Font, KeyboardFocusManager
from java.awt.event import KeyAdapter, KeyEvent
from com.infinitekind.moneydance.model import AccountUtil
from com.moneydance.apps.md.view.gui import MoneydanceGUI

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
        
        # Build UI on Event Dispatch Thread for thread safety
        SwingUtilities.invokeLater(self.build_ui)

    def build_ui(self):
        # 2. Build the Swing UI components
        # Get the currently active window to act as parent for the modal JDialog
        active_window = KeyboardFocusManager.getCurrentKeyboardFocusManager().getActiveWindow()
        
        # Using JDialog instead of JFrame for a modal, integrated experience
        # If active_window is a Frame or Dialog, Jython handles the overloaded constructor
        try:
            self.dialog = JDialog(active_window, "Jump to Account", True)
        except TypeError:
            # Fallback if active_window is null or incompatible
            self.dialog = JDialog()
            self.dialog.setTitle("Jump to Account")
            self.dialog.setModal(True)
            
        self.dialog.setSize(500, 350)
        self.dialog.setLocationRelativeTo(active_window) # Center on parent frame
        self.dialog.setLayout(BorderLayout())
        self.dialog.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE)
        
        self.search_field = JTextField()
        self.search_field.setFont(Font("SansSerif", Font.PLAIN, 16))
        self.search_field.setBorder(BorderFactory.createCompoundBorder(
            self.search_field.getBorder(), 
            BorderFactory.createEmptyBorder(5, 5, 5, 5)))
            
        self.list_model = DefaultListModel()
        self.account_list_ui = JList(self.list_model)
        self.account_list_ui.setFont(Font("SansSerif", Font.PLAIN, 14))
        
        scroll_pane = JScrollPane(self.account_list_ui)
        scroll_pane.setBorder(BorderFactory.createEmptyBorder())
        
        # Populate the initial list with all accounts
        self.current_matches = list(self.all_accounts)
        self.update_list_view()
        
        # Add components to the dialog
        self.dialog.add(self.search_field, BorderLayout.NORTH)
        self.dialog.add(scroll_pane, BorderLayout.CENTER)
        
        # 3. Attach keyboard listeners for fluid, mouseless navigation
        class JumpKeyListener(KeyAdapter):
            def __init__(self, switcher):
                self.switcher = switcher
                
            def keyReleased(self, event):
                self.switcher.handle_key_released(event)
                
        self.search_field.addKeyListener(JumpKeyListener(self))
        
        self.dialog.setVisible(True)
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
                
                # Close switcher window BEFORE navigating
                self.dialog.dispose() 
                
                # Use the recommended API to switch the existing view to the selected account register
                try:
                    mdGUI = MoneydanceGUI.getInstance()
                    mdGUI.showAccountTransactionView(target_account)
                except Exception as e:
                    print "Error navigating to account:", e
                
        # Escape closes the window
        elif code == KeyEvent.VK_ESCAPE:
            self.dialog.dispose()
            
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
    # Initialize the UI switcher instance
    QuickAccountSwitcher(moneydance, book)
except NameError:
    print "Error: This script must be executed inside the Moneydance Moneybot Console."