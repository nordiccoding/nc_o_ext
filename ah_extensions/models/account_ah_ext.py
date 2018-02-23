# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
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

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """ finalize_invoice_move_lines(move_lines) -> move_lines

            Hook method to be overridden in additional modules to verify and
            possibly alter the move lines to be created by an invoice, for
            special cases.
            :param move_lines: list of dictionaries with the account.move.lines (as for create())
            :return: the (possibly updated) final move_lines to create for this invoice
        """
        for m in move_lines:

            if m[2]["name"] =="Inv Ref: n.a.":
                m[2]["name"] = "! xxxx !"
            
        return move_lines


    @api.multi
    def action_move_create(self):
        """ To get the vendor invoice number included into AML """
        account_move = self.env['account.move']



        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or 'inv nr needs to go here!'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        #and here same as below
                        'name': 'Inv Ref: %s' % (inv.reference if inv.reference else 'n.a.'), 
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    #added this to get the inv. number included in AML
                    'name': 'Inv Ref: %s' % (inv.reference if inv.reference else 'n.a.'), 
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv



            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)


        return True


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




