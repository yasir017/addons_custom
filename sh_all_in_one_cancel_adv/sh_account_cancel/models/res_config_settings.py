# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    invoice_operation_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_draft', 'Cancel and Reset to Draft'), ('cancel_delete', 'Cancel and Delete')],
                                              default='cancel', string="Invoice Operation Type")

    payment_operation_type = fields.Selection([('cancel', 'Cancel Only'), ('cancel_draft', 'Cancel and Reset to Draft'), ('cancel_delete', 'Cancel and Delete')],
                                              default='cancel', string="Payment Operation Type")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_operation_type = fields.Selection(string="Invoice Operation Type",related="company_id.invoice_operation_type", readonly=False)

    payment_operation_type = fields.Selection(string="Payment Operation Type",related="company_id.payment_operation_type", readonly=False)
