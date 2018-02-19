README FILE
===========

Extensions for accounting.

Manual steps
------------

- When creating the database do so in German, and load English afterwards. Loading the database in English (and with country Germany) 
  causes the translations to be laoded twice and not then always with correct translations (since these are overwritten).
- Install the apps (before installing and switching to English)

- Install SKR03 or SKR04, Install Sales + Finance
- In accounting settings change the default VAT settings. Allow multi currencies in general settings. Load language DE. 
  change time zone. Change date format and commas. Change inter-bank transfer account, VAT defaults, set CoA number of digits
- Go to settings and search for the view Journal Items, give the accountant the role.
- Change the date so that Europeans can read it (%d.%m.%Y) also in English translation.
- Remove the € currency signs from the views. Do this by coing to configuration options
  and add a space in place of the symbol (blank field is not allowed). THIS SEEM NOT TO
  WORK => it will remove the currency sign in the reports/invoices.

I did do following for local currnce (hack must be fixed!)

```javascript

          // odoo/addons/web/static/src/js/views/list_viws.js after line 1990 ColumnMonetary

            //when the curremcy is € we do not need to see the symbol
            //so short cirquit and return
            if (currency.symbol==='€') {
                return value;
            }
```

Some added info data ...

Costcenter by Onestein (https://www.odoo.com/apps/modules/10.0/account_cost_center/
                        git clone https://github.com/onesteinbv/addons-onestein.git)

Install account_move_template, web_export_view (https://github.com/OCA/web.git),
account_fiscal_position_vat_check (https://github.com/OCA/account-financial-tools.git),
https://github.com/OCA/account-payment.git -> account_due_list,
https://github.com/OCA/bank-payment.git
https://github.com/OCA/server-tools.git -> this is for user managment
        
Load Language DE
Import Bank
Import partners
Logo

pip install unidecode (required for banking plain)

Create Bank Verrechnungskonto 1365 and Journal (type Purchase)


Installed / changed features
----------------------------

Add the field *acctive* (was removed from v9) back to the chart of accounts. This is 
very usefull if you have alot of un-needed accounts.

Add the field *note* back to the view for internal notes and comments.

Right allign debit, credit and amount in tree views.

Widen the modal forms.

Reorder fields in Journal Items List View



Fiscal Positions
----------------

The field VAT Required in Fiscal Positions must be checked for the correct VAT to be calculated. Also if partner
is both supplier and customer a fiscal position should be created for both tax treastments.




Account Move and Account Move Lines
-----------------------------------

The field Ref in AM and AML must be made mandatory, when s supplier invoice entered the supplier inv. code comes here,
when an out-going invoice (when from company initiated statement) then internal ref must be filled by code/sequence (duplicate info).

TODO: The forward / when posting invoice must be removed and substitued for Ref. Nr.


Multi Currency
--------------

To get multi currency to work properly so that the foreign currency is correctly calculated and posted you must go 
to the currencies and initiate the first rate for all currencies with the same time stamp.


Test Data
---------



Bank setup
----------

Creditor Identifier for testing purposes: DE98ZZZ09999999999
source ( https://www.bundesbank.de/Redaktion/EN/Standardartikel/Tasks/Payment_systems/sepa_creditor_identifier.html )


Bank Reconciliation
-------------------

The bank reconciliation is done by importing the bank statements and then reconciling these against entries posted. Odoo will 
go a long way in assisting with the process. 

*Reconciliation Models*
Reconciliation models are quick buttons that can be added to the bank reconciliation widget to ease and speed the reconcilliation process. A use case
would be if discount is offered on swift payment (say of 2%). A quick button can be added for this in the following manner; Make a copy of the standard VAT Rate
and call it VAT tax inclusive. Go to the advanced option and set "included in price" option. In the "Reconciliation Models" for your bank account (under more option in dashboard)
you create a new reconciliation model. Create a payment term with 30 Days and 2% discount, do not split the payment for customers as you only want the terms and do not want to receivable to be spli over several lines. 

*link_bank_to_partner*
link_bank_to_partner (will change the partner of a bank account) and must removed. comment out _complete_statement from OCA module account_bank_statement_import. This part was used to find partner and his bank account and it was creating bank accounts if they weren't found in the system. Odoo function link_bank_to_partner. This function re-links bank account to a partner if they appeared in bank statement line, and partner on the bank statement is different than the partner on bank account. This is happening after reconciliation, and after closing of bank statement.



Excellent Links
---------------

https://akhmadkresna.github.io/posts/odoo-custom-field
