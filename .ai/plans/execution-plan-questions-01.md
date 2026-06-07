# Execution Plan Clarification Questions

Please answer the following questions to help clarify the execution plan and design requirements before we proceed.

## Question 1

For the requirement in Phase 1 to address the bug where selecting an account opens a new Moneydance window instead of navigating within the existing one, how should the script determine which window is the "existing" or "previously active" window?

A) Use the main/primary Moneydance frame (typically the first frame returned by the application).

B) Use the window/frame that was active/focused immediately before the search dialog was opened.

C) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 2

For Phase 2, how should the Python script be packaged and integrated as a Moneydance extension?

A) Package it as a standard `.mxt` file containing the python script, assets, and a `meta_info.dict` file.

B) Keep it as a standalone `.py` script, but run it through a custom setup or provide instructions on triggering it.

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3

If we package the project as a `.mxt` extension in Phase 2, what extension ID and menu name/label should we use?

A) ID: `quick_account_switcher`, Label: "Quick Account Switcher"

B) ID: `jump_to_account`, Label: "Jump to Account"

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4

When searching for accounts, should the search query match against the full hierarchical path (e.g. "Assets:Bank:Chase Checking") or only the final/leaf account name (e.g. "Chase Checking")?

A) Match against the full hierarchical path (e.g., searching "Bank" will show the Checking account under Bank).

B) Match only against the final/leaf account name (e.g., searching "Bank" will not show Checking unless "Bank" is in its name, ignoring parent names).

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5

For the multi-word filtering in Phase 3, how should the search terms be matched?

A) Order-independent match: All entered terms must be present, but they can appear in any order (e.g., "ch ba" matches both "Chase Bank" and "Bank Checking").

B) Order-dependent match: Entered terms must appear in the exact order typed, though not necessarily adjacent (e.g., "ch ba" matches "Chase Bank" but not "Bank Chase").

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 6

Should Moneydance categories (Income and Expense categories, which are represented as `Account` objects under the hood) be included in the search results alongside standard accounts (Bank, Credit Card, Asset, Liability, Loan)?

A) Yes, include both standard accounts and categories.

B) No, include only standard accounts and exclude categories.

C) Other (please describe after [Answer]: tag below)

[Answer]: C - Include standard accounts, investment accounts, assets, and loans. Do not include categories.
