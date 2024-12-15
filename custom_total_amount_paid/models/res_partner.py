from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_amount_paid_pos = fields.Monetary(
        string='Total Amount Paid (POS)',
        compute='_compute_total_amount_paid_pos',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('pos_order_ids')
    def _compute_total_amount_paid_pos(self):
        for partner in self:
            total_paid = sum(
                order.amount_total
                for order in self.env['pos.order'].search([('partner_id', '=', partner.id)])
            )
            partner.total_amount_paid_pos = total_paid
