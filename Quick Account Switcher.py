global moneydance                           # Entry point into the Moneydance API
mdGUI = moneydance.getUI()                  # Entry point into the GUI
book = moneydance.getCurrentAccountBook()   # Entry point into your dataset

import sys
from javax.swing import AbstractAction, KeyStroke, JComponent, JDialog, JTextField, JList, JScrollPane, DefaultListModel, SwingUtilities, WindowConstants, BorderFactory
from java.awt import BorderLayout, Font, KeyboardFocusManager, Toolkit
from java.awt.event import KeyAdapter, KeyEvent, InputEvent
from com.infinitekind.moneydance.model import AccountUtil

class LaunchMessageAction(AbstractAction):
    def __init__(self, extension_instance):
        AbstractAction.__init__(self)
        self.ext = extension_instance

    def actionPerformed(self, event):
        try:
            # Trigger the standard invocation path
            self.ext.invoke("popup")
        except Exception as e:
            import traceback
            traceback.print_exc(file=sys.stderr)

class QuickAccountSwitcherExtension(object):

    def initialize(self, extension_context, extension_object):
        self.moneydanceContext = extension_context
        self.moneydanceExtensionObject = extension_object

        # Bind the keyboard hooks to the active window pane
        self.setup_keyboard_shortcuts()

    def invoke(self, eventString=""):
        self.moneydanceContext.setStatus("Python extension received command: %s" % (eventString))

        if eventString=='popup':
            self.all_accounts = []
            self.enable_selection = False
            for acct in AccountUtil.getAccountIterator(book):
                # Exclude the root account itself
                if acct.getParentAccount():
                    self.all_accounts.append(acct)
            
            # Sort accounts alphabetically by their full display name
            self.all_accounts.sort(key=lambda x: x.getFullAccountName().lower())
            
            # Build UI on Event Dispatch Thread for thread safety
            SwingUtilities.invokeLater(self.build_ui)

    def setup_keyboard_shortcuts(self):
        active_window = mdGUI.getFirstMainFrame()
        if not active_window or active_window.getClass().getSimpleName() != "MainFrame":
            return

        root_pane = active_window.getRootPane()
        action_key = "LaunchSimpleMessageExtension"

        toolkit = Toolkit.getDefaultToolkit()
        modifier = toolkit.getMenuShortcutKeyMaskEx() | InputEvent.SHIFT_DOWN_MASK
        precise_stroke = KeyStroke.getKeyStroke(KeyEvent.VK_J, modifier)

        # Pass 'self' (the extension instance) to the action listener
        root_pane.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(precise_stroke, action_key)
        root_pane.getActionMap().put(action_key, LaunchMessageAction(self))


    def __str__(self):
        return "QuickAccountSwitcher"


    def build_ui(self):
        # 2. Build the Swing UI components
        # Get the currently active window to act as parent for the modal JDialog
        self.active_window = KeyboardFocusManager.getCurrentKeyboardFocusManager().getActiveWindow()
        
        # Using JDialog instead of JFrame for a modal, integrated experience
        # If active_window is a Frame or Dialog, Jython handles the overloaded constructor
        try:
            self.dialog = JDialog(self.active_window, "Jump to Account", True)
        except TypeError:
            # Fallback if active_window is null or incompatible
            self.dialog = JDialog()
            self.dialog.setTitle("Jump to Account")
            self.dialog.setModal(True)
            
        self.dialog.setSize(500, 350)
        self.dialog.setLocationRelativeTo(self.active_window) # Center on parent frame
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
            if self.enable_selection:
                idx = self.account_list_ui.getSelectedIndex()
                if idx >= 0:
                    target_account = self.current_matches[idx]
                    # Use the direct API to switch the view to the selected account
                    # HACK: unsupported API - https://infinitekind.tenderapp.com/discussions/moneydance-development/13732-ui-selection
                    main_frame = mdGUI.getFirstMainFrame()
                    main_frame.selectAccount(target_account)
                    self.dialog.dispose() # Close switcher window
            else:
                self.enable_selection = True
                
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

# Tell moneydance this is an extension
moneydance_extension =  QuickAccountSwitcherExtension()

