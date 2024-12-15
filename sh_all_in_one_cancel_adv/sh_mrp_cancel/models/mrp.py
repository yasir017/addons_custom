# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

import re
from odoo import models


class Production(models.Model):
    _inherit = 'mrp.production'

    def action_mrp_cancel(self):
        for rec in self:
            if self.company_id.cancel_child_mo:
                domain = [('origin', '=', rec.name)]
                find_child_mo = self.env['mrp.production'].search(domain)
                if find_child_mo:
                    for data in find_child_mo:
                        data.action_mrp_cancel()
            rec.process_action_mrp_cancel()

    def process_action_mrp_cancel(self):
        """
        The function cancels a manufacturing order and all related moves, work orders, and pickings.
        """
        self.ensure_one()
        self.sudo().mapped('move_finished_ids').action_move_cancel()

        self.sudo().mapped('move_raw_ids').action_move_cancel()

        self.sudo().mapped('workorder_ids').leave_id.unlink()
        self.sudo().mapped('workorder_ids').end_all()
        self.sudo().workorder_ids.write({
            'date_planned_start': False,
            'date_planned_finished': False,
            'state':'cancel'
        })

        self.sudo().mapped('move_dest_ids').action_move_cancel()
        self.sudo().mapped('picking_ids').action_picking_cancel()

        self.qty_producing = 0
        self.sudo().action_cancel()

    def action_mrp_cancel_draft(self):
        """
        The function cancels draft manufacturing orders and their child orders if the company setting
        allows it.
        """
        for rec in self:
            if self.company_id.cancel_child_mo:
                domain = [('origin', '=', rec.name)]
                find_child_mo = self.env['mrp.production'].search(domain)
                if find_child_mo:
                    for data in find_child_mo:
                        data.action_mrp_cancel_draft()
            rec.process_action_mrp_cancel_draft()

    def process_action_mrp_cancel_draft(self):
        """
        The function cancels and resets various moves, work orders, and pickings associated with a
        manufacturing order.
        """
        self.ensure_one()
        self.sudo().mapped('move_finished_ids').action_move_cancel_draft()
        self.sudo().mapped('move_finished_ids').quantity_done = 0
        self.sudo().mapped('move_finished_ids.move_line_ids').unlink()

        self.sudo().mapped('move_raw_ids').action_move_cancel_draft()
        self.sudo().mapped('move_raw_ids').quantity_done = 0
        self.sudo().mapped('move_raw_ids').manual_consumption = False
        self.sudo().mapped('move_raw_ids.move_line_ids').unlink()

        self.sudo().mapped('workorder_ids').leave_id.unlink()
        self.sudo().mapped('workorder_ids').end_all()
        self.sudo().workorder_ids.write({
            'date_planned_start': False,
            'date_planned_finished': False,
            'state':'waiting'
        })

        self.sudo().mapped('move_dest_ids').action_move_cancel_draft()
        self.sudo().mapped('move_dest_ids').quantity_done = 0
        self.sudo().mapped('move_dest_ids.move_line_ids').unlink()
        self.sudo().mapped('picking_ids').action_picking_cancel_draft()
        # rec.sudo().product_uom_id = False
        # rec.product_qty = 0
        self.qty_producing = 0
        self.sudo().state = False

    def action_mrp_cancel_delete(self):
        """
        This function cancels and deletes a manufacturing order and its child orders if the company
        setting allows it.
        """
        for rec in self:
            if self.company_id.cancel_child_mo:
                domain = [('origin', '=', rec.name)]
                find_child_mo = self.env['mrp.production'].search(domain)
                if find_child_mo:
                    for data in find_child_mo:
                        data.action_mrp_cancel_delete()
            rec.process_action_mrp_cancel_delete()
        

    def process_action_mrp_cancel_delete(self):
        """
        This function cancels and deletes a manufacturing order and its related moves, work orders, and
        pickings.
        """
        self.ensure_one()
        self.sudo().mapped('move_finished_ids').action_move_cancel_draft()
        self.sudo().mapped('move_finished_ids').quantity_done = 0
        self.sudo().mapped('move_finished_ids.move_line_ids').unlink()
        raw_moves = self.sudo().mapped('move_raw_ids')
        raw_moves.action_move_cancel_draft()
        raw_moves.quantity_done = 0
        raw_moves.manual_consumption = False
        self.sudo().mapped('move_raw_ids.move_line_ids').unlink()

        self.sudo().mapped('workorder_ids').leave_id.unlink()
        self.sudo().mapped('workorder_ids').end_all()
        self.sudo().workorder_ids.write({
            'date_planned_start': False,
            'date_planned_finished': False,
            'state':'waiting'
        })

        self.sudo().mapped('move_dest_ids').action_move_cancel_draft()
        self.sudo().mapped('move_dest_ids').quantity_done = 0
        self.sudo().mapped('move_dest_ids.move_line_ids').unlink()
        self.sudo().mapped('picking_ids').action_picking_cancel_draft()
        self.sudo().unlink()

        return {
            'name': 'Manufacturing Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def sh_cancel(self):
        """
        This function cancels a manufacturing order and its child orders if specified, based on the
        company's chosen cancellation operation type.
        """
        if self.company_id.cancel_child_mo:
            domain = [('origin', '=', self.name)]
            find_child_mo = self.env['mrp.production'].search(domain)
            if find_child_mo:
                for data in find_child_mo:
                    data.sh_cancel()
        if self.company_id.mrp_operation_type == 'cancel':
            self.process_action_mrp_cancel()
        elif self.company_id.mrp_operation_type == 'cancel_draft':
            self.process_action_mrp_cancel_draft()
        elif self.company_id.mrp_operation_type == 'cancel_delete':
            return self.process_action_mrp_cancel_delete()
        return True
