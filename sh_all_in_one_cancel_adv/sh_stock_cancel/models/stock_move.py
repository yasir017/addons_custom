# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class Move(models.Model):
    _inherit = 'stock.move'

    def _check_stock_account_installed(self):
        stock_account_app = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'stock_account')], limit=1)
        if stock_account_app.state != 'installed':
            return False
        else:
            return True

    def _sh_unreseve_qty(self):
        if self.state != 'done':
            self.do_unreserve()
        for move_line in self.sudo().mapped('move_ids_without_package').mapped('move_line_ids'):
            if move_line.product_id.detailed_type == 'consu':
                continue
            # Check qty is not in draft and cancel state
            if self.state not in ['draft','cancel','assigned','waiting'] :
                
                # unreserve qty
                quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                               ('product_id', '=', move_line.product_id.id),
                                                               ('lot_id', '=', move_line.lot_id.id),
                                                               ('package_id', '=', move_line.package_id.id),
                                                               ], limit=1)
    
                if quant:
                    quant.write({'quantity': quant.quantity + move_line.qty_done})
                else:
                    self.env['stock.quant'].sudo().create({'location_id': move_line.location_id.id,
                                                            'product_id': move_line.product_id.id,
                                                            'lot_id': move_line.lot_id.id,
                                                            'quantity': move_line.qty_done,
                                                            # 'package_id': move_line.package_id.id
                                                            })
                quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                               ('product_id', '=', move_line.product_id.id),
                                                               ('lot_id', '=', move_line.lot_id.id),
                                                               ('package_id', '=', move_line.result_package_id.id),
                                                               ], limit=1)
                if quant:
                    quant.write({'quantity': quant.quantity - move_line.qty_done})
                else:
                    self.env['stock.quant'].sudo().create({'location_id': move_line.location_dest_id.id,
                                                            'product_id': move_line.product_id.id,
                                                            'lot_id':move_line.lot_id.id,
                                                            'quantity':move_line.qty_done * (-1),
                                                            # 'package_id': move_line.result_package_id.id 
                                                            })

    def action_move_cancel(self):
        for rec in self:
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'cancel'})
            rec.mapped('move_line_ids').sudo().write({'state': 'cancel'})

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(
                    ['|', ('credit_move_id', 'in', reconcile_ids), ('debit_move_id', 'in', reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped(
                    'line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state': 'draft', 'name': '/'})
                account_move.sudo().with_context(
                    {'force_delete': True}).unlink()

                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()

    def action_move_cancel_draft(self):
        for rec in self:
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(
                    ['|', ('credit_move_id', 'in', reconcile_ids), ('debit_move_id', 'in', reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped(
                    'line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state': 'draft', 'name': '/'})
                account_move.sudo().with_context(
                    {'force_delete': True}).unlink()

                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()

    def action_move_cancel_delete(self):
        for rec in self:
            rec._sh_unreseve_qty()
            rec.sudo().write({'state': 'draft'})
            rec.mapped('move_line_ids').sudo().write({'state': 'draft'})

            if rec._check_stock_account_installed():
                # cancel related accouting entries
                account_move = rec.sudo().mapped('account_move_ids')
                account_move_line_ids = account_move.sudo().mapped('line_ids')
                reconcile_ids = []
                if account_move_line_ids:
                    reconcile_ids = account_move_line_ids.sudo().mapped('id')
                reconcile_lines = self.env['account.partial.reconcile'].sudo().search(
                    ['|', ('credit_move_id', 'in', reconcile_ids), ('debit_move_id', 'in', reconcile_ids)])
                if reconcile_lines:
                    reconcile_lines.sudo().unlink()
                account_move.mapped(
                    'line_ids.analytic_line_ids').sudo().unlink()
                account_move.sudo().write({'state': 'draft', 'name': '/'})
                account_move.sudo().with_context(
                    {'force_delete': True}).unlink()

                # cancel stock valuation
                stock_valuation_layer_ids = rec.sudo().mapped('stock_valuation_layer_ids')
                if stock_valuation_layer_ids:
                    stock_valuation_layer_ids.sudo().unlink()

            rec.mapped('move_line_ids').sudo().unlink()
            rec.sudo().unlink()
