# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """
    This is an Odoo model for configuration settings. It inherits from the
    'res.config.settings' model and extends its functionality by adding
    fields for low stock alert configuration

    """
    _inherit = 'res.config.settings'

    product_quantity_limit = fields.Boolean(
        string="Product Quantity Limit",
        help="Enable if you want to limit product quantity in point of sale or invoice",
        related='pos_config_id.product_quantity_limit',
        readonly=False, store=True, config_parameter='nthub_pos_product_quantity_limit.product_quantity_limit')

    product_quantity_limit_type = fields.Selection([('pos', 'POS'), ('both', 'POS and Invoice')],
                                                   string='Product Quantity Limit Type', default='pos',
                                                   related='pos_config_id.product_quantity_limit_type',
                                                   readonly=False, store=True,
                                                   config_parameter='nthub_pos_product_quantity_limit.product_quantity_limit_type')

    is_pos_bill_quantity_limit = fields.Boolean(
        string="Enable POS Bill Quantity Limit",
        help="Enable if you want to limit quantity in point of sale bill",
        related='pos_config_id.is_pos_bill_quantity_limit', readonly=False, store=True
    )
    pos_bill_quantity_limit = fields.Integer(
        string="POS Bill Quantity Limit",
        help="Enter the quantity limit for POS bill",
        related='pos_config_id.pos_bill_quantity_limit', readonly=False, store=True
    )

    # @api.onchange('product_quantity_limit')
    # def _onchange_product_quantity_limit(self):
    #     """The function is used to change the stock alert in the product form"""
    #     if self.env['ir.config_parameter'].sudo().get_param(
    #             'nthub_pos_product_quantity_limit.product_quantity_limit'):
    #         product_variants = self.env['product.product'].search([])
    #         for rec in product_variants:
    #             rec.is_product_quantity_limit = True
    #     else:
    #         product_variants = self.env['product.product'].search([])
    #         for rec in product_variants:
    #             rec.is_product_quantity_limit = False
