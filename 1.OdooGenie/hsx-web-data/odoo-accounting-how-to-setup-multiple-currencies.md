Source: https://hsxtech.net/odoo-accounting-how-to-setup-multiple-currencies/

# Odoo Accounting: How to Setup Multiple Currencies in Odoo Accounting

Handling money in various currencies can be a huge task for business organizations that have operations globally. Odoo Accounting’s multi-currency module is a boon in such a scenario. Odoo’s robust solutions make handling various currencies, exchange rates, and the accounting work involved, a cakewalk.
If you are an entrepreneur, an accountant, or you use Odoo, this manual will guide you on how to install and use Odoo Accounting with multiple currencies. You will be able to streamline and simplify your accounting at the end.

## Why Use Odoo Accounting for Multi-Currency Transactions?

Odoo Accounting is a robust solution for companies that have customers, suppliers, or partners in various currencies. With the multi-currency feature, you can:

- Monitor transactions in foreign currencies.
- Automate exchange rate refresh.
- Simply balance exchange rate gains or losses.
- Create precise financial reports with multi-currency reconciliation.

## How to activate and configure Multiple Currencies in Odoo Accounting

### Step 1: Activate the Multi-Currency Function
- Log into your Odoo account as an administrator.
- Navigate to Settings under the “General Settings” menu.
- Under the Accounting Section, locate the “Multi-Currency” option.
- Toggle the setting to “On.”
- Save your changes.

### Step 2: Set Up Your Currencies
Next, define which currencies your business will use. To do this:

1. Go to Accounting &gt; Configuration &gt; Currencies.
2. Click Create to add a new currency.
3. Input the currency details:

    - Currency Code (e.g., USD, EUR, GBP).
    - Symbol (e.g., $, €, £).
    - Current Rate (the current exchange rate for this currency).

4. Save your currency configurations.

### Step 3: Assign Currencies to Accounts and Partners

Once currencies are set up, assign them to:

- Bank Accounts:
        - Go to Accounting &gt; Configuration &gt; Bank Accounts.
        - Select a bank account and set a specific currency for it.
- Partners (Customers &amp; Suppliers):
        - Navigate to Sales &gt; Customers or Purchases &gt; Vendors.
        - Choose the relevant partner and define their default currency under the “Sales &amp; Purchases” section.

Setting currencies at the partner level ensures transactions in Odoo will default to the appropriate currency, avoiding costly conversion errors.


## Configure Exchange Rate Gain/Loss Accounts

Currency fluctuations can lead to gains or losses when you convert foreign transactions into your company’s base currency. To account for these, configure Exchange Rate Gain and Loss Accounts in Odoo.

### Step 1: Create Gain/Loss Accounts
1. Navigate to Accounting &gt; Configuration &gt; Chart of Accounts.
2. Create two new accounts:

        - Currency Exchange Gain Account (Profit and Loss category).
        - Currency Exchange Loss Account (Profit and Loss category).


1. Go to Accounting &gt; Configuration &gt; Settings.
2. Under the “Default Accounts” section, specify:

        - The Exchange Rate Gain Account.
        - The Exchange Rate Loss Account.

3. Save your changes.

This setup ensures Odoo automatically records exchange rate variances in the appropriate accounts.


## Take the Next Step in Streamlining Your Accounting

Configuring Odoo Accounting for multiple currencies may seem complex at first glance, but with the right guidance, the process is remarkably straightforward. Following the steps outlined above will ensure your accounting system is set up for success, no matter where in the world your business operates.

Need assistance optimizing your Odoo setup? We’re here to help! Book a consultation with our Odoo Implementation experts and ensure your accounting process is operating at peak efficiency.
