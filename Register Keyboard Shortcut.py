import sys
from java.awt import Toolkit
from java.awt.event import KeyEvent, InputEvent
from java.beans import PropertyChangeListener
from java.awt import KeyboardFocusManager
from javax.swing import AbstractAction, KeyStroke, JComponent

# 1. Define the Action mapping to call the extension's invoke method
class LaunchMessageAction(AbstractAction):
    def __init__(self, extension_instance):
        AbstractAction.__init__(self)
        self.ext = extension_instance

    def actionPerformed(self, event):
        try:
            self.ext.invoke("show_msg")
        except Exception as e:
            import traceback
            traceback.print_exc(file=sys.stderr)

# 2. Focus listener to automatically catch new or switched windows
class WindowFocusTracker(PropertyChangeListener):
    def __init__(self, extension_instance):
        self.ext = extension_instance

    def propertyChange(self, event):
        # Listen specifically for changes in the active window
        if event.getPropertyName() == "activeWindow":
            new_window = event.getNewValue()
            if new_window and new_window.getClass().getSimpleName() == "MainFrame":
                # Inject the shortcut into the newly focused frame if it isn't there
                self.ext.register_shortcut_on_frame(new_window)

# 3. Define the Extension lifecycle controller
class SimpleMessageExtension(object):
    def __init__(self):
        self.context = None
        self.md_ui = None
        self.focus_listener = None

    def initialize(self, extension_context, extension_object):
        """
        Moneydance automatically executes this method when loading the extension.
        """
        self.context = extension_context
        self.md_ui = extension_context.getUI()
        
        # Bind to the primary window immediately
        primary_win = self.md_ui.getFirstMainFrame()
        if primary_win:
            self.register_shortcut_on_frame(primary_win)
        
        # Start tracking focus globally to catch new windows opened later
        self.focus_listener = WindowFocusTracker(self)
        kfm = KeyboardFocusManager.getCurrentKeyboardFocusManager()
        kfm.addPropertyChangeListener("activeWindow", self.focus_listener)

    def invoke(self, event_string):
        """
        Moneydance automatically triggers this when the user clicks the menu item.
        """
        if event_string in ["show_msg", ""]:
            self.md_ui.showInfoMessage("Hello! You triggered this via the unified invocation method.")

    def register_shortcut_on_frame(self, frame):
        """
        Safely registers the shortcut mapping on a specific frame's root pane.
        """
        root_pane = frame.getRootPane()
        action_key = "LaunchSimpleMessageExtension"

        # Check if already registered on this specific component map to prevent duplicates
        input_map = root_pane.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW)
        
        toolkit = Toolkit.getDefaultToolkit()
        modifier = toolkit.getMenuShortcutKeyMaskEx() | InputEvent.SHIFT_DOWN_MASK
        precise_stroke = KeyStroke.getKeyStroke(KeyEvent.VK_J, modifier)

        if input_map.get(precise_stroke) is None:
            input_map.put(precise_stroke, action_key)
            root_pane.getActionMap().put(action_key, LaunchMessageAction(self))

    def unload(self):
        """
        Cleanup hook to remove listeners if the extension is disabled or reloaded.
        """
        if self.focus_listener:
            kfm = KeyboardFocusManager.getCurrentKeyboardFocusManager()
            kfm.removePropertyChangeListener("activeWindow", self.focus_listener)

    def __str__(self):
        return "Simple Message Shortcut Extension"

# 4. The Registration Hook
global moneydance_extension
moneydance_extension = SimpleMessageExtension()