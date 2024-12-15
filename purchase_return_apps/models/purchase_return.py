# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import datetime, time


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_return_boolean = fields.Boolean(string='Return')
    purchase_return = fields.One2many('purchase.return.line', 'purchase_id')
    purchase_return_ids_count = fields.Integer(string="Return Count", compute="action_purchase_return_ids_count")

    def purchase_return_button(self):
        view_id = self.env['purchase.return.wizard']
        order_line = []
        if self.product_id:
            for variable in self.order_line:
                vals = (0, 0, {
                    'product_id': variable.product_id.id,
                    'product': variable.name,
                    'org_qty': variable.qty_received,
                    'price_unit': variable.price_unit,
                    'price_subtotal': variable.price_subtotal,
                    'currency_id': self.env.user.company_id.currency_id.id,
                })
                order_line.append(vals)
        ctx = {
            'default_purchase_contact_line_ids': order_line,
        }

        return {
            'type': 'ir.actions.act_window',
            'name': 'PURCHASE RETURN',
            'res_model': 'purchase.return.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id.id,
            'view_id': self.env.ref('purchase_return_apps.purchase_return_related_wizard',
                                    False).id,
            'context': ctx,
            'target': 'new',
        }

    def action_purchase_return_box(self):
        self.sudo().ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        form_view = self.sudo().env.ref('purchase_return_apps.purchase_return_order_form')
        tree_view = self.sudo().env.ref('purchase_return_apps.view_purchase_return_tree')
        return {
            'name': _('Return Purchase Order'),
            'res_model': 'purchase.return.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('reference', '=', self.name)],
        }

    def action_purchase_return_ids_count(self):
        count = self.env['purchase.return.order'].sudo().search_count([('reference', '=', self.name)])
        self.purchase_return_ids_count = count


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    quantity_return = fields.Float('Returned', digits='Product Unit of Measure')

    # @api.depends('product_qty', 'price_unit', 'taxes_id', 'qty_received', 'quantity_return')
    # def _compute_amount(self):
    #     for line in self:
    #         taxes = line.taxes_id.compute_all(**line._prepare_compute_all_values())
    #         tax_val = taxes['total_included'] - taxes['total_excluded']
    #         total = float(tax_val) * float(line.qty_received * line.price_unit)
    #         sub_total = line.qty_received * line.price_unit
    #         line.update({
    #             'price_tax': tax_val,
    #             'price_total': total,
    #             'price_subtotal': sub_total,
    #         })


class purchase_return_wizard(models.TransientModel):
    _name = 'purchase.return.wizard'
    _description = 'Purchase Return Wizard'

    remarks = fields.Text('Purchase Return')
    purchase_contact_line_ids = fields.One2many('purchase.return.wizard.line',
                                                'purchase_contact_id',
                                                string='Return Products')
    return_date = fields.Datetime(string='Date Of Return')
    user_name = fields.Many2one('res.users', string='Purchase Representative')
    reason = fields.Char(string="Reason")

    def tick_ok(self):
        return_purchase = self.env['purchase.return.order']
        applicant_id = self._context.get('active_ids')[0]
        active_id = self.env['purchase.order'].sudo().search([('id', '=', applicant_id)])
        count = 0
        list = [(4, 0, 0)]
        if self.purchase_contact_line_ids:
            for i in self.purchase_contact_line_ids:
                for j in active_id.order_line:
                    if i.product_id.id == j.product_id.id:
                        received = i.replace_qty
                        return_qty = float(j.product_qty - j.qty_received) + float(i.quantity)
                        j.qty_received = received
                        j.quantity_return = return_qty

            return_vals = {
                'date': self.return_date,
                'partner_id': self.user_name.id,
                'reason': self.reason,
            }
            list.append((0, 0, return_vals))
            active_id.purchase_return = list

            return_line = [(5, 0, 0)]
            for i in self.purchase_contact_line_ids:
                vals = {
                    'product_id': i.product_id.id,
                    'org_qty': i.quantity + i.replace_qty,
                    'replace_qty': i.quantity,
                    'price_unit': i.price_unit,
                }
                return_line.append((0, 0, vals))

            datas = {
                'vendor': self.user_name.id,
                'partner_id': active_id.partner_id.id,
                'stock_picking_type': active_id.picking_type_id.id,
                'return_date': self.return_date,
                'reason': self.reason,
                'reference': active_id.name,
                'return_lines': return_line,
            }
            return_purchase.sudo().create(datas)

        else:
            raise UserError(_('Alert!, Dear %s, you cannot select multiple contacts to create Patients '
                              'registration') % self.env.user.name)
        return True


class purchase_return_wizard_line(models.TransientModel):
    _name = 'purchase.return.wizard.line'
    _description = 'Purchase Return Wizard Line'

    purchase_contact_id = fields.Many2one('purchase.return.wizard')
    product_id = fields.Many2one('product.product', string='Purchase')
    name = fields.Char(string='Name')
    product = fields.Char(string="Product")
    qty = fields.Float(string="Orginal Quantity")
    quantity = fields.Float(string="Replace Quantity")
    org_qty = fields.Float(string="OnHand Qty")
    replace_qty = fields.Float(string="Quantity")
    price_unit = fields.Float('Unit Price')
    price_subtotal = fields.Monetary(string='Subtotal')
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.onchange('quantity')
    def replace_quantity(self):
        self.write({
            'replace_qty': self.org_qty - self.quantity,
        })
        self.write({
            'price_subtotal': self.replace_qty * self.price_unit,
        })


class PurchaseReturnLine(models.Model):
    _name = 'purchase.return.line'
    _description = 'Purchase Return Line'

    date = fields.Datetime(string='Date Of Return')
    name = fields.Char(string="Reference")
    partner_id = fields.Many2one("res.users")
    reason = fields.Char(string='Reason')
    # product_id = fields.Many2one('product.template')
    purchase_id = fields.Many2one('purchase.order')

    @api.model
    def create(self, vals):
        vals["name"] = (
                self.env["ir.sequence"].next_by_code("purchase.return.line") or "New"
        )
        return super(PurchaseReturnLine, self).create(vals)


class StockPiciking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        id = self.env['purchase.order'].search([('id', '=', self.purchase_id.id)])

        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_ids and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.qty_done, precision_rounding=move_line.product_uom_id.rounding) for move_line
                in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
                    products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda
                                                 m: m.product_id.type == 'product' and m.state != 'cancel' and m.qty_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search(
                    [('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.ids),
                     ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                    ('qty_done', '>', 0),
                    ('location_id', 'in', wh_location_ids),
                    ('move_orig_ids', '=', False),
                    ('picking_id', 'not in', self.ids),
                    ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action

        id.purchase_return_boolean = True
        return True