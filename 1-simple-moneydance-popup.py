from com.infinitekind.moneydance.model import *
import os
from javax.swing import JButton, JFrame, JScrollPane, JTextArea, BoxLayout, BorderFactory

class SimplePopupExtension(object):

    def initialize(self, extension_context, extension_object):
	self.moneydanceContext = extension_context
	self.moneydanceExtensionObject = extension_object

	# here we register ourselves with a menu item to invoke a feature
	# (ignore the button and icon mentions in the docs)
	self.moneydanceContext.registerFeature(extension_object, "popup", None, "Test popup")
        
    # invoke(eventstring) is called when we receive a callback for the feature that
    # we registered in the initialize method
    def invoke(self, eventString=""):
	self.moneydanceContext.setStatus("Python extension received command: %s" % (eventString))

        if eventString=='popup':
            self._show_popup()

    def __str__(self):
	return "SimplePopup"

    # Our actual user code
    def _show_popup(self):
        self._initUI()
        book = moneydance.getCurrentAccountBook()
        account_names = []
        for acct in AccountUtil.getAccountIterator(book):
            account_names.append(acct.getFullAccountName())
        self.text_area.text = '\n'.join(account_names)

    def _initUI(self):
        frame = JFrame('Simple popup', defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE, size=(300,300))
        frame.setLayout(BoxLayout(frame.contentPane, BoxLayout.PAGE_AXIS))
        # Call-back to close popup
        def closeDialog(event):
            frame.visible = False
            frame.dispose()

        # Instantiate components
        self.text_area = JTextArea()
        msgScroller = JScrollPane()                                                                                                                                                                                                              
        msgScroller.setBorder(BorderFactory.createTitledBorder("Accounts"))
        msgScroller.setViewportView(self.text_area)
        self.close_button = JButton('Close', actionPerformed = closeDialog)

        # Add components to frame
        frame.add(msgScroller)
        frame.add(self.close_button)
        frame.visible = True


# Tell moneydance this is an extension
moneydance_extension = SimplePopupExtension()

