# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class Move(models.Model):
    _inherit = 'stock.move'

    def _sh_unreseve_qty(self):
        for res in self:
            # Check qty is not in draft and cancel state
            if self.sudo().mapped('picking_id').state not in ['draft', 'cancel', 'assigned', 'waiting']:

                # Check qty is not in draft and cancel state
                if res.state not in ['draft', 'cancel']:

                    for move_line in self.sudo().mapped('move_line_ids'):
                        # unreserve qty
                        quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_id.id),
                                                                       ('product_id', '=',
                                                                        move_line.product_id.id),
                                                                       ('lot_id', '=', move_line.lot_id.id)], limit=1)

                        if quant:
                            quant.write(
                                {'quantity': quant.quantity + move_line.qty_done})

                        quant = self.env['stock.quant'].sudo().search([('location_id', '=', move_line.location_dest_id.id),
                                                                       ('product_id', '=',
                                                                        move_line.product_id.id),
                                                                       ('lot_id', '=', move_line.lot_id.id)], limit=1)

                        if quant:
                            quant.write(
                                {'quantity': quant.quantity - move_line.qty_done})
