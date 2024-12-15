from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    main_vendor_id = fields.Many2one(
        'res.partner', string='Main Vendor', compute='_compute_main_vendor', store=True)

    @api.depends('seller_ids')
    def _compute_main_vendor(self):
        for product in self:
            if product.seller_ids:
                product.main_vendor_id = product.seller_ids[0].partner_id
            else:
                product.main_vendor_id = False
