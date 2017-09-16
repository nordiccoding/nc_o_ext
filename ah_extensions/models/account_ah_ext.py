# -*- coding: utf-8 -*-
from openerp import models, fields

class AccountAccount(models.Model):

    _inherit = 'account.account'
    _description = "Account Extended"
    
    active = fields.Boolean(index=True, default=True, help="""When False will hide the account from all views.
                                                            To see de-activated fields again you must use the filters in list view.""")