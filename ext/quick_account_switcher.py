import sys
from javax.swing import AbstractAction, KeyStroke, JComponent, JDialog, JTextField, JList, JScrollPane, DefaultListModel, SwingUtilities, WindowConstants, BorderFactory
from java.awt import BorderLayout, Font, KeyboardFocusManager, Toolkit, Window
from java.awt.event import KeyAdapter, KeyEvent, InputEvent
from java.beans import PropertyChangeListener
from com.infinitekind.moneydance.model import AccountUtil

class LaunchMessageAction(AbstractAction):
    def __init__(self, extension_instance, frame):
        AbstractAction.__init__(self)
        self.ext = extension_instance
        self.frame = frame

    def actionPerformed(self, event):
        try:
            # Pass the specific frame that received the shortcut trigger
            self.ext.invoke("shortcut", target_frame=self.frame)
        except Exception as e:
            import traceback
            traceback.print_exc(file=sys.stderr)

class WindowFocusTracker(PropertyChangeListener):
    def __init__(self, extension_instance):
        self.ext = extension_instance

    def propertyChange(self, event):
        if event.getPropertyName() == "activeWindow":
            new_window = event.getNewValue()
            if new_window and new_window.getClass().getSimpleName() == "MainFrame":
                self.ext.register_shortcut_on_frame(new_window)


class QuickAccountSwitcherExtension(object):

    def __init__(self):
        self.focus_listener = None
        self.trigger_frame = None
        self.active = False

    def initialize(self, extension_context, extension_object):
        self.moneydanceContext = extension_context
        self.moneydanceExtensionObject = extension_object

        self.active = True
        # Startup can precede both the GUI and dataset. Watch for windows first.
        self.focus_listener = WindowFocusTracker(self)
        kfm = KeyboardFocusManager.getCurrentKeyboardFocusManager()
        kfm.addPropertyChangeListener("activeWindow", self.focus_listener)
        SwingUtilities.invokeLater(self.register_existing_windows)

    def register_existing_windows(self):
        if self.active:
            for window in Window.getWindows():
                if window.getClass().getSimpleName() == "MainFrame":
                    self.register_shortcut_on_frame(window)

    def invoke(self, eventString="", target_frame=None):
        if not self.active:
            return
        book = self.moneydanceContext.getCurrentAccountBook()
        if book is None:
            return
        self.enable_selection = True

        # Capture the context frame. Fall back to current keyboard focus if launched via top menu.
        if target_frame:
            self.trigger_frame = target_frame
        else:
            active_win = KeyboardFocusManager.getCurrentKeyboardFocusManager().getActiveWindow()
            if active_win and active_win.getClass().getSimpleName() == "MainFrame":
                self.trigger_frame = active_win
            else:
                self.trigger_frame = self.moneydanceContext.getUI().getFirstMainFrame()

        if eventString == 'popup':
            self.enable_selection = False

        if eventString in ['popup', 'shortcut']:
            self.all_accounts = []
            for acct in AccountUtil.getAccountIterator(book):
                if acct.getParentAccount() and not acct.accountIsInactive:
                    self.all_accounts.append(acct)
            
            self.all_accounts.sort(key=lambda x: x.getFullAccountName().lower())
            SwingUtilities.invokeLater(self.build_ui)

    def register_shortcut_on_frame(self, frame):
        """
        Safely registers the shortcut mapping on a specific frame's root pane.
        """
        if not self.active:
            return
        if not SwingUtilities.isEventDispatchThread():
            SwingUtilities.invokeLater(lambda: self.register_shortcut_on_frame(frame))
            return
        root_pane = frame.getRootPane()
        action_key = "quick_account_switcher.launch"

        input_map = root_pane.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW)

        toolkit = Toolkit.getDefaultToolkit()
        modifier = toolkit.getMenuShortcutKeyMaskEx() | InputEvent.SHIFT_DOWN_MASK
        precise_stroke = KeyStroke.getKeyStroke(KeyEvent.VK_J, modifier)

        if input_map.get(precise_stroke) is None:
            input_map.put(precise_stroke, action_key)
            root_pane.getActionMap().put(action_key, LaunchMessageAction(self, frame))

    def handle_event(self, eventString):
        if eventString == "md:file:opened":
            SwingUtilities.invokeLater(self.register_existing_windows)

    def unload(self):
        self.active = False
        if self.focus_listener:
            kfm = KeyboardFocusManager.getCurrentKeyboardFocusManager()
            kfm.removePropertyChangeListener("activeWindow", self.focus_listener)
            self.focus_listener = None
        SwingUtilities.invokeLater(self.remove_shortcuts)

    def remove_shortcuts(self):
        for window in Window.getWindows():
            if window.getClass().getSimpleName() != "MainFrame":
                continue
            root = window.getRootPane()
            action_key = "quick_account_switcher.launch"
            action = root.getActionMap().get(action_key)
            if isinstance(action, LaunchMessageAction) and action.ext is self:
                input_map = root.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW)
                for stroke in input_map.keys() or []:
                    if input_map.get(stroke) == action_key:
                        input_map.remove(stroke)
                root.getActionMap().remove(action_key)
        self.trigger_frame = None
        self.all_accounts = []
        self.current_matches = []
        if getattr(self, "dialog", None) is not None:
            self.dialog.dispose()
            self.dialog = None

    def __str__(self):
        return "QuickAccountSwitcher"

    def build_ui(self):
        if not self.active:
            return
        try:
            self.dialog = JDialog(self.trigger_frame, "Jump to Account", True)
        except TypeError:
            self.dialog = JDialog()
            self.dialog.setTitle("Jump to Account")
            self.dialog.setModal(True)
            
        self.dialog.setSize(500, 350)
        self.dialog.setLocationRelativeTo(self.trigger_frame)
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
        
        self.current_matches = list(self.all_accounts)
        self.update_list_view()
        
        self.dialog.add(self.search_field, BorderLayout.NORTH)
        self.dialog.add(scroll_pane, BorderLayout.CENTER)
        
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
                
        elif code == KeyEvent.VK_ENTER:
            if self.enable_selection:
                idx = self.account_list_ui.getSelectedIndex()
                if idx >= 0:
                    target_account = self.current_matches[idx]
                    
                    # Call selectAccount directly on the active target frame
                    if self.trigger_frame:
                        self.trigger_frame.selectAccount(target_account)
                        
                    self.dialog.dispose()
            else:
                self.enable_selection = True
                
        elif code == KeyEvent.VK_ESCAPE:
            self.dialog.dispose()
            
        else:
            search_text = self.search_field.getText().lower()
            self.current_matches = [
                acct for acct in self.all_accounts 
                if search_text in acct.getFullAccountName().lower()
            ]
            self.update_list_view()

# Tell moneydance this is an extension
moneydance_extension = QuickAccountSwitcherExtension()
