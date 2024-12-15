# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_stock_installed(self):
        stock_app = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'stock')], limit=1)
        if stock_app.state != 'installed':
            return False
        else:
            return True

    def action_sale_cancel(self):
        for rec in self:
            if rec.company_id.cancel_delivery :
                rec.sudo().mapped('picking_ids').action_picking_cancel()
            if rec.company_id.cancel_invoice:
                if rec.mapped('invoice_ids'):
                    if rec.mapped('invoice_ids'):
                        move = rec.mapped('invoice_ids')
                        move_line_ids = move.sudo().mapped('line_ids')
                        reconcile_ids = []
                        if move_line_ids:
                            reconcile_ids = move_line_ids.sudo().mapped('id')
                        reconcile_lines = self.env[
                            'account.partial.reconcile'].sudo().search([
                                '|', ('credit_move_id', 'in', reconcile_ids),
                                ('debit_move_id', 'in', reconcile_ids)
                            ])
                        payments = False
                        if reconcile_lines:
                            payments = self.env['account.payment'].search([
                                '|',
                                ('invoice_line_ids.id', 'in',
                                 reconcile_lines.mapped('credit_move_id').ids),
                                ('invoice_line_ids.id', 'in',
                                 reconcile_lines.mapped('debit_move_id').ids)
                            ])

                            reconcile_lines.sudo().unlink()

                            if payments:

                                payment_ids = payments
                                if payment_ids.sudo().mapped('move_id').mapped(
                                        'line_ids'):
                                    payment_lines = payment_ids.sudo().mapped(
                                        'move_id').mapped('line_ids')
                                    reconcile_ids = payment_lines.sudo(
                                    ).mapped('id')

                        reconcile_lines = self.env[
                            'account.partial.reconcile'].sudo().search([
                                '|', ('credit_move_id', 'in', reconcile_ids),
                                ('debit_move_id', 'in', reconcile_ids)
                            ])
                        if reconcile_lines:
                            reconcile_lines.sudo().unlink()
                        move.mapped(
                            'line_ids.analytic_line_ids').sudo().unlink()

                        move_line_ids.sudo().write({'parent_state': 'draft'})
                        move.sudo().write({'state': 'draft'})

                        if payments:
                            payment_ids = payments
                            payment_ids.sudo().mapped('move_id').write(
                                {'state': 'draft'})
                            payment_ids.sudo().mapped('move_id').mapped(
                                'line_ids').sudo().write(
                                    {'parent_state': 'draft'})
                            payment_ids.sudo().mapped('move_id').mapped(
                                'line_ids').sudo().unlink()

                            payment_ids.sudo().write({'state': 'cancel'})

                            payment_ids.sudo().mapped('move_id').with_context({
                                'force_delete':
                                True
                            }).unlink()

                    rec.mapped('invoice_ids').sudo().write({'state': 'cancel'})
            rec.sudo().write({'state': 'cancel'})

    def action_sale_cancel_draft(self):
        for rec in self:
            if rec.company_id.cancel_delivery :
                rec.sudo().mapped('picking_ids').action_picking_cancel_draft()

            if rec.company_id.cancel_invoice:
                if rec.mapped('invoice_ids'):
                    if rec.mapped('invoice_ids'):
                        move = rec.mapped('invoice_ids')
                        move_line_ids = move.sudo().mapped('line_ids')

                        reconcile_ids = []
                        if move_line_ids:
                            reconcile_ids = move_line_ids.sudo().mapped('id')

                        reconcile_lines = self.env[
                            'account.partial.reconcile'].sudo().search([
                                '|', ('credit_move_id', 'in', reconcile_ids),
                                ('debit_move_id', 'in', reconcile_ids)
                            ])
                        payments = False
                        if reconcile_lines:
                            payments = self.env['account.payment'].search([
                                '|',
                                ('invoice_line_ids.id', 'in',
                                 reconcile_lines.mapped('credit_move_id').ids),
                                ('invoice_line_ids.id', 'in',
                                 reconcile_lines.mapped('debit_move_id').ids)
                            ])

                            reconcile_lines.sudo().unlink()

                            if payments:
                                if payments.sudo().mapped('move_id').mapped(
                                        'line_ids'):
                                    payment_lines = payments.sudo().mapped(
                                        'move_id').mapped('line_ids')
                                    reconcile_ids = payment_lines.sudo(
                                    ).mapped('id')

                        reconcile_lines = self.env[
                            'account.partial.reconcile'].sudo().search([
                                '|', ('credit_move_id', 'in', reconcile_ids),
                                ('debit_move_id', 'in', reconcile_ids)
                            ])
                        if reconcile_lines:
                            reconcile_lines.sudo().unlink()
                        move.mapped(
                            'line_ids.analytic_line_ids').sudo().unlink()

                        move_line_ids.sudo().write({'parent_state': 'draft'})
                        move.sudo().write({'state': 'draft'})

                        if payments:
                            payment_ids = payments
                            payment_ids.sudo().mapped('move_id').write(
                                {'state': 'draft'})
                            payment_ids.sudo().mapped('move_id').mapped(
                                'line_ids').sudo().write(
                                    {'parent_state': 'draft'})
                            payment_ids.sudo().mapped('move_id').mapped(
                                'line_ids').sudo().unlink()
                            payment_ids.sudo().write({'state': 'cancel'})
                            #                             payment_ids.sudo().unlink()
                            payment_ids.sudo().mapped('move_id').with_context({
                                'force_delete':
                                True
                            }).unlink()

                    rec.mapped('invoice_ids').sudo().write({'state': 'draft'})
            rec.sudo().write({'state': 'draft'})

    def action_sale_cancel_delete(self):
        for rec in self:
            if rec.company_id.cancel_delivery:
                rec.sudo().mapped('picking_ids').action_picking_cancel_delete()

            if rec.company_id.cancel_invoice:

                if rec.mapped('invoice_ids'):
                    if rec.mapped('invoice_ids'):
                        move = rec.mapped('invoice_ids')
                        move_line_ids = move.sudo().mapped('line_ids')

                        reconcile_ids = []
                        if move_line_ids:
                            reconcile_ids = move_line_ids.sudo().mapped('id')

                        reconcile_lines = self.env[
                            'account.partial.reconcile'].sudo().search([
                                '|', ('credit_move_id', 'in', reconcile_ids),
                                ('debit_move_id', 'in', reconcile_ids)
                            ])
                        payments = False
                        if reconcile_lines:

                            payments = self.env['account.payment'].search([
                                '|',
                                ('invoice_line_ids.id', 'in',
                                 reconcile_lines.mapped('credit_move_id').ids),
                                ('invoice_line_ids.id', 'in',
                                 reconcile_lines.mapped('debit_move_id').ids)
                            ])
                            reconcile_lines.sudo().unlink()
                            if payments:
                                payment_ids = payments
                                if payment_ids.sudo().mapped('move_id').mapped(
                                        'line_ids'):
                                    payment_lines = payment_ids.sudo().mapped(
                                        'move_id').mapped('line_ids')
                                    reconcile_ids = payment_lines.sudo(
                                    ).mapped('id')

                        reconcile_lines = self.env[
                            'account.partial.reconcile'].sudo().search([
                                '|', ('credit_move_id', 'in', reconcile_ids),
                                ('debit_move_id', 'in', reconcile_ids)
                            ])
                        if reconcile_lines:
                            reconcile_lines.sudo().unlink()
                        move.mapped(
                            'line_ids.analytic_line_ids').sudo().unlink()

                        move_line_ids.sudo().write({'parent_state': 'draft'})
                        move.sudo().write({'state': 'draft'})

                        if payments:
                            payment_ids = payments
                            payment_ids.sudo().mapped('move_id').write(
                                {'state': 'draft'})
                            payment_ids.sudo().mapped('move_id').mapped(
                                'line_ids').sudo().write(
                                    {'parent_state': 'draft'})
                            payment_ids.sudo().mapped('move_id').mapped(
                                'line_ids').sudo().unlink()

                            payment_ids.sudo().write({'state': 'cancel'})
                            #                             payment_ids.sudo().unlink()
                            payment_ids.sudo().mapped('move_id').with_context({
                                'force_delete':
                                True
                            }).unlink()

                    rec.mapped('invoice_ids').sudo().write({'state': 'draft'})
                    rec.mapped('invoice_ids').sudo().with_context({
                        'force_delete':
                        True
                    }).unlink()

            rec.sudo().write({'state': 'cancel'})

        for rec in self:
            rec.sudo().unlink()

    def sh_cancel(self):
        """
        This function checks the operation type of a company and performs a corresponding action on a
        sale order.
        """
        if self.company_id.operation_type == 'cancel':
            self.action_sale_cancel()
        elif self.company_id.operation_type == 'cancel_draft':
            self.action_sale_cancel_draft()
        elif self.company_id.operation_type == 'cancel_delete':
            self.action_sale_cancel_delete()
            return {
                'name': 'Quotations',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_type': 'form',
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'target': 'current',
                'context': {
                    'search_default_my_quotation': 1
                }
            }
