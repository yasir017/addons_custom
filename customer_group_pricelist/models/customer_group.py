# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Prathyunnan R (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, api


class CustomerGroup(models.Model):
    """New model to create customer group price list."""
    _name = 'customer.group'
    _description = 'Create Customer Groups'

    name = fields.Char(string='Name', help='Name of the Pricelist')
    contact_ids = fields.Many2many('res.partner', string='Contacts',
                                   help='Add contacts to the customer group')
    pricelist_id = fields.Many2one('product.pricelist', string='PriceList',
                                   help='Add Pricelist for apply on the '
                                        'customer group')


"""
class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_group_name = fields.Char(
        string="Customer Group",
        related='customer_group_id.name',  # Assuming there's a customer_group_id Many2one field in res.partner
        readonly=True
    )
"""
class ResPartnercust(models.Model):
    _inherit = 'res.partner'

    customer_group_ids = fields.Many2many('customer.group', string='Customer Groups',
                                          help='Customer groups this contact belongs to')
    
    customer_group_name = fields.Char(string='Customer Group Name', store=True,
                                      compute='_compute_customer_group_name', help='Name of the first customer group')

    @api.depends('customer_group_ids')
    def _compute_customer_group_name(self):
        for record in self:
            if record.customer_group_ids:
                record.customer_group_name = record.customer_group_ids[0].name
            else:
                record.customer_group_name = ''
