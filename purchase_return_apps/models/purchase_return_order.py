from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import datetime, time


class PurchaseReturnOrder(models.Model):
    _name = 'purchase.return.order'
    _description = 'Purchase Returns Order'

    def _get_stock_type_ids(self):
        data = self.env['stock.picking.type'].search([])
        for line in data:
            if line.name == 'Delivery Orders' and line.sequence_code == 'OUT':
                self.stock_picking_type = line.id

    name = fields.Char(string='Name')
    vendor = fields.Many2one('res.users', string='Purchase Representative')
    return_date = fields.Datetime(string='Date Of Return')
    reason = fields.Char(string="Reason")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed')], default='draft')
    reference = fields.Char(string='Reference')
    return_lines = fields.One2many('purchase.return.order.line', 'return_relation')
    purchase_return_confirm_ids = fields.Integer(string='Return', compute='return_count')
    partner_id = fields.Many2one('res.partner', string='Customer')
    stock_picking_type = fields.Many2one('stock.picking.type', string='Operation Type', compute='_get_stock_type_ids')
    invoice_picking_id = fields.Many2one('stock.picking', string="Picking Id", copy=False)
    purchase_return_invoice = fields.Integer(string="Debit Note", compute='purchase_return_credit_note_count')

    def purchase_return_credit_note_count(self):
        count = self.env['account.move'].sudo().search_count([('narration', '=', self.name)])
        self.purchase_return_invoice = count

    @api.model
    def create(self, vals):
        vals["name"] = (
                self.env["ir.sequence"].next_by_code("purchase.return.order") or "New"
        )
        return super(PurchaseReturnOrder, self).create(vals)

    def return_count(self):
        count = self.env['stock.picking'].sudo().search_count([('origin', '=', self.name)])
        self.purchase_return_confirm_ids = count

    def purchase_return_confirm_button(self):
        return_line = [(5, 0, 0)]
        for i in self.return_lines:
            line_val = {
                'product_id': i.product_id.id,
                'quantity_done': i.replace_qty,
                'name': i.product_id.name,
                'product_uom': i.product_id.uom_po_id,
                'product_uom_qty': i.replace_qty,
                'location_id': self.partner_id.property_stock_supplier.id,
                'location_dest_id': self.partner_id.property_stock_supplier.id,

            }
            return_line.append((0, 0, line_val))

        data = {
            'picking_type_id': self.stock_picking_type.id,
            'partner_id': self.partner_id.id,
            'scheduled_date': self.return_date,
            'origin': self.name,
            'move_ids_without_package': return_line,
            'location_id': self.partner_id.property_stock_supplier.id,
            'location_dest_id': self.partner_id.property_stock_supplier.id,
        }
        self.env['stock.picking'].sudo().create(data)

        self.write({
            'state': 'confirm',
        })

    def action_stock_move(self):
        if not self.stock_picking_type:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.invoice_picking_id:
                pick = {}
                if self.stock_picking_type.code == 'outgoing':
                    pick = {
                        'picking_type_id': order.stock_picking_type.id,
                        'partner_id': order.partner_id.id,
                        'origin': order.name,
                        'location_dest_id': order.partner_id.property_stock_customer.id,
                        'location_id': order.stock_picking_type.default_location_src_id.id,
                        'move_type': 'direct'
                    }
                self.write({'state': 'confirm'})
                picking = self.env['stock.picking'].create(pick)
                self.invoice_picking_id = picking.id
                self.purchase_return_confirm_ids = len(picking)
                moves = order.return_lines.filtered(
                    lambda r: r.product_id.type in ['product', 'consu'])._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                move_ids._action_assign()

    def action_purchase_return_button_box(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('stock.view_picking_form')
        tree_view = self.sudo().env.ref('stock.vpicktree')
        return {
            'name': _('Return Purchase Order'),
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('origin', '=', self.name)],
        }

    def create_vendor_credit(self):
        """This is the function for creating refund
                from the purchase return"""
        if self.stock_picking_type.code == 'outgoing':
            invoice_line_list = []
            for purchase_returns in self.return_lines:
                vals = (0, 0, {
                    'name': purchase_returns.product_id.name,
                    'product_id': purchase_returns.product_id.id,
                    'price_unit': purchase_returns.price_unit,
                    'account_id': purchase_returns.product_id.property_account_income_id.id if purchase_returns.product_id.property_account_income_id
                    else purchase_returns.product_id.categ_id.property_account_income_categ_id.id,
                    'quantity': purchase_returns.replace_qty,
                })
                invoice_line_list.append(vals)
            invoice = self.env['account.move'].sudo().create({
                'move_type': 'in_refund',
                'invoice_origin': self.name,
                'narration': self.name,
                'partner_id': self.partner_id.id,
                'currency_id': self.env.user.company_id.currency_id.id,
                'journal_id': 2,
                'payment_reference': self.name + '(' + self.reference + ')',
                'ref': self.name,
                'invoice_line_ids': invoice_line_list
            })
            return invoice

    def action_open_picking_invoice(self):
        """This is the function of the smart button which redirect to the
        invoice related to the current picking"""
        return {
            'name': 'Supplier Credit',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('narration', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }


class PurchaseReturnOrderLine(models.Model):
    _name = 'purchase.return.order.line'
    _description = 'Purchase Returns Order Line'

    product_id = fields.Many2one('product.template')
    org_qty = fields.Float(string="OnHand Qty")
    replace_qty = fields.Float(string="Replace Quantity")
    return_relation = fields.Many2one("purchase.return.order")
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Monetary(string='Subtotal')
    currency_id = fields.Many2one('res.currency', string='Currency')

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if picking.picking_type_id.code == 'outgoing':
                template = {
                    'name': line.product_id.name or '',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.return_relation.partner_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'picking_type_id': picking.picking_type_id.id,
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
                diff_quantity = line.replace_qty
                tmp = template.copy()
                tmp.update({
                    'product_uom_qty': diff_quantity,
                })
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done
