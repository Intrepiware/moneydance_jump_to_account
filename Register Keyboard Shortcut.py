import sys
from java.awt import Toolkit
from java.awt.event import KeyEvent, InputEvent
from javax.swing import AbstractAction, KeyStroke, JComponent

# 1. Define the Action mapping to call the extension's invoke method
class LaunchMessageAction(AbstractAction):
    def __init__(self, extension_instance):
        AbstractAction.__init__(self)
        self.ext = extension_instance

    def actionPerformed(self, event):
        try:
            # Trigger the standard invocation path
            self.ext.invoke("show_msg")
        except Exception as e:
            import traceback
            traceback.print_exc(file=sys.stderr)

# 2. Define the Extension lifecycle controller
class SimpleMessageExtension(object):
    def __init__(self):
        self.context = None
        self.md_ui = None

    def initialize(self, extension_context, extension_object):
        """
        Moneydance automatically executes this method when loading the extension.
        """
        self.context = extension_context
        
        # Capture the UI environment
        self.md_ui = extension_context.getUI()
        
        # Bind the keyboard hooks to the active window pane
        self.setup_keyboard_shortcuts()

    def invoke(self, event_string):
        """
        Moneydance automatically triggers this when the user clicks the menu item.
        """
        # Accept the "show_msg" string or the default/empty string sent by the menu click
        if event_string in ["show_msg", ""]:
            self.md_ui.showInfoMessage("Hello! You triggered this via the unified invocation method.")

    def setup_keyboard_shortcuts(self):
        active_window = self.md_ui.getFirstMainFrame()
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
        return "Simple Message Shortcut Extension"

# 3. The Registration Hook
# Setting this global variable instructs the interpreter to register the class
global moneydance_extension
moneydance_extension = SimpleMessageExtension()