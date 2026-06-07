# Moneydance Account Quick Jump Tool

## Overview

Moneydance lacks a native way to jump to an account in the active window using only keyboard shortcuts. This forces the user to use the mouse, which may disrupt certain workflows.

## Goal

We'd like to create a Moneydance extension that will allow the user to jump to any account using just keyboard shortcuts.

## Design

When the user presses the keyboard shortcut, a modal window should be displayed that presents a list of the accounts in Moneydance and a search box. The search box acts as an autosuggest: as the user types in search criteria, the list of displayed accounts is filtered to match the characters the user has entered.

When the user selects an account, the _previously active_ window is navigated to the Transaction view of the selected account.
