# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class AccountAccount(models.Model):

    _inherit = 'account.account'
    _description = "Account Extended"
    
    #
    #    active = fields.Boolean(index=True, default=True, help="""When False will hide the account from all views.
    #                                                       To see de-activated fields again you must use the filters in list view.""")

    kennziffer = fields.Char(string='Kennziffer', translate=True, help="""The number to be used in the German VAT return.""")




class AccountBankStatement(models.Model):

    _inherit = 'account.bank.statement'
    _description = "Remove the linking of partner in bank statements when reconciling."


    @api.multi
    def link_bank_to_partner(self):
        #raise("This should not be executed, it gets called from button_confirm_bank .... ")
        print "method link_bank_to_partner has been deprecated ...."
        pass



class AccountInvoice(models.Model):
    """To force the entry of an invoice number when invoice is received."""

    _inherit = "account.invoice"
    _description = "Invoice"


    def _check_invoice_reference(self):
        for invoice in self:
            #refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            #because it's probably a double encoding of the same bill/refund
            
            #if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
            #when removing the and inv.reference we make ref mandatory!

            if invoice.type in ('in_invoice', 'in_refund'):
                if not invoice.reference:
                    raise UserError(_("Vendor reference or invoice number is required."))

                if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
                    raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))



class AccountJournal(models.Model):

    _inherit = 'account.journal'
    _description = """If you want to create a bank statement manually then an error is raised when the company is not set in bank. However
    you cannot set this in the bank since you then will not be able to make inter-company payments."""


    @api.one
    @api.constrains('type', 'bank_account_id')
    def _check_bank_account(self):
        if self.type == 'bank' and self.bank_account_id:
            if self.bank_account_id.company_id != self.company_id:
                #raise ValidationError(_('The bank account of a bank journal must belong to the same company (%s).') % self.company_id.name)
                print "The validation error was removed -> The bank account of a bank journal must belong to the same company"
            # A bank account can belong to a customer/supplier, in which case their partner_id is the customer/supplier.
            # Or they are part of a bank journal and their partner_id must be the company's partner_id.
            if self.bank_account_id.partner_id != self.company_id.partner_id:
                raise ValidationError(_('The holder of a journal\'s bank account must be the company (%s).') % self.company_id.name)



class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.one
    @api.constrains('payment_method_id', 'journal_id')
    def _check_bank_account(self):
        
        print "Now overriding the enterprise version of _check_bank_account"

        if self.payment_method_id == self.env.ref('account_sepa.account_payment_method_sepa_ct'):
            if not self.journal_id.bank_account_id or not self.journal_id.bank_account_id.acc_type == 'iban':
                raise ValidationError(_("The journal '%s' requires a proper IBAN account to pay via SEPA. Please configure it first.") % self.journal_id.name)
            if not self.journal_id.bank_account_id.bank_bic:
                raise ValidationError(_("The account '%s' (journal %s) requires a Bank Identification Code (BIC) to pay via SEPA. Please configure it first.")
                    % (self.journal_id.bank_account_id.acc_number, self.journal_id.name))




