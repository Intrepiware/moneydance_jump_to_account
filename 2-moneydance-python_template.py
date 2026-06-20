#!/usr/bin/env python
# Python script to be run in Moneydance to perform amazing feats of financial scripting.

global moneydance                           # Entry point into the Moneydance API
mdGUI = moneydance.getUI()                  # Entry point into the GUI
book = moneydance.getCurrentAccountBook()   # Entry point into your dataset

import sys, platform
from java.lang import System
from com.infinitekind.moneydance.model import *
if moneydance.getBuild() >= 5100: from com.infinitekind.util import AppDebug

print("")
print("Java version:              %s" %(System.getProperty("java.version")))
print("Py(Jy)thon platform:       %s %s %s.%s" %(platform.python_implementation(), platform.system(), sys.version_info.major, sys.version_info.minor))
print("")
print("Moneydance version:        MD%s(%s)" %(moneydance.getVersion(), moneydance.getBuild()))
print("The Moneydance controller: %s >> (the global variable 'moneydance' accesses this key object)" %(moneydance))
print("The UI:                    %s" %(mdGUI))
print("The current data set:      '%s'" %(book))

if book is not None:
    tSet = book.getTransactionSet()
    allAccounts = AccountUtil.allMatchesForSearch(book, AcctFilter.ALL_ACCOUNTS_FILTER)
    print("")
    print("Number of transactions in this dataset: %s" %(tSet.getTransactionCount()))
    print("Number of Accounts:                     %s" %(len([a for a in allAccounts if not a.getAccountType().isCategory() and a.getAccountType() != Account.AccountType.ROOT])))
    print("Number of Categories:                   %s" %(len([a for a in allAccounts if a.getAccountType().isCategory()])))
    print("------")
    msgStr = "Hello world... Printing to Moneydance's console from this python script...."
    if moneydance.getBuild() >= 5100:
        AppDebug.ALL.log(msgStr)        # This is how you write to the Moneydance Console (post MD2024)
    else:
        System.err.println(msgStr)      # This is how you write to the Moneydance Console (pre MD2024)

    counter = 0
    for txn in tSet:
        if counter < 10:
            print("transaction: date %s: description: %s for amount %s"
                  % (txn.getDateInt(), txn.getDescription().ljust(35, " "),
                     txn.getAccount().getCurrencyType().formatFancy(txn.getValue(), ".").rjust(20, " ")))
            counter += 1


class ExampleExtension:
    def __init__(self):
        self.myContext = None
        self.myExtensionObject = None

    # The initialize method is called when the extension is loaded and provides the
    # extension's context. The 'context' implements the methods defined in the FeatureModuleContext:
    # http://infinitekind.com/dev/apidoc/com/moneydance/apps/md/controller/FeatureModuleContext.html
    def initialize(self, extension_context, extension_object):
        self.myContext = extension_context
        self.myExtensionObject = extension_object
        
        # here we register ourselves with an Extension's menu item to invoke a feature (ignore the button and icon mentions in the docs)
        self.myContext.registerFeature(extension_object, "doSomethingCool", None, "Do Something Cool!")
        System.err.println("ExampleExtension registered as an extension...")

    # invoke(eventString) is called when we receive a callback for the feature that we registered in the initialize method
    def invoke(self, eventString=""):
        msg = "Python extension received command: %s" % (eventString)
        self.myContext.setStatus(msg)
        System.err.println(msg)

    # handle_event(eventString) is called whenever Moneydance fires a system event...
    def handle_event(self, eventString=""):
        cmd, param = self.decodeCommand(eventString)
        msg = "Python extension observed Moneydance event: %s - cmd: '%s' param: '%s'" %(eventString, cmd, param)
        self.myContext.setStatus(msg)
        System.err.println(msg)

    def __str__(self): return "ExampleExtension"    # This is the Python equivalent of toString() below
    def __repr__(self): return self.__str__()
    def toString(self): return self.__str__()       # This is needed for java to call

    def decodeCommand(self, passedEvent):
        param = ""
        uri = passedEvent
        command = uri
        theIdx = uri.find('?')
        if(theIdx>=0):
            command = uri[:theIdx]
            param = uri[theIdx+1:]
        else:
            theIdx = uri.find(':')
            if(theIdx>=0):
                command = uri[:theIdx]
                param = uri[theIdx+1:]
        return command, param


# setting the "moneydance_extension" variable tells Moneydance to register that object as an extension
# NOTE: This will only do anything / install when running as a script. It will NOT work when running as a snippet!
moneydance_extension = ExampleExtension()
