# -*- coding: utf-8 -*-

from odoo import api, fields, models

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
        raise("This should not be executed, it gets called from button_confirm_bank .... ")


