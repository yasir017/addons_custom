# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang


class account_move(models.Model):
	_inherit = 'account.move'

	invoice_line_ids = fields.One2many(  # /!\ invoice_line_ids is just a subset of line_ids.
		'account.move.line',
		'move_id',
		string='Invoice lines',
		copy=False,
		readonly=True,
		domain=[('display_type', 'in', ('product', 'line_section', 'line_note')),('exclude_from_invoice_tab', '=', False)],
		states={'draft': [('readonly', False)]},
	)
	is_line = fields.Boolean('Is a line')

   

	@api.depends('discount_amount','discount_method','discount_type','config_inv_tax')
	def _calculate_discount(self):
		res_config= self.env.company
		cur_obj = self.env['res.currency']
		res=0.0
		discount = 0.0
		for move in self:
			applied_discount = line_discount = sums = move_discount =  amount_untaxed = amount_tax = amount_after_discount =  0.0
			if self._context.get('default_move_type') in ['out_invoice', 'out_receipt', 'out_refund']:
				if res_config.tax_discount_policy:
					if res_config.tax_discount_policy == 'tax':
						if move.discount_method == 'fix':
							discount = move.discount_amount
							res = discount
						elif move.discount_method == 'per':
							total = 0.0
							tax = 0.0
							for line in self.invoice_line_ids:
								if line.exclude_from_invoice_tab == False:
									tax += line.com_tax()
									total += line.price_unit 
								res = (total + tax) * (move.discount_amount/ 100)
						else:
							res = discount


						for line in move.invoice_line_ids:
							amount_untaxed += line.price_subtotal
							applied_discount += line.discount_amt
				
							if line.discount_method == 'fix':
								line_discount += line.discount_amount
								res = line_discount
							elif line.discount_method == 'per':
								tax = line.com_tax()
								line_discount += (line.price_subtotal + tax)  * (line.discount_amount/ 100)
								res = line_discount

					else:

						for line in move.invoice_line_ids:
							amount_untaxed += line.price_subtotal
							applied_discount += line.discount_amt
							res = applied_discount
				
							if line.discount_method == 'fix':
								line_discount += line.discount_amount
								res = line_discount
							elif line.discount_method == 'per':
								# tax = line.com_tax()
								line_discount += line.price_subtotal * (line.discount_amount/ 100)
								res = line_discount

						if move.discount_type == 'global':
							if move.discount_method == 'fix':
								move_discount = move.discount_amount
								res = move_discount
								if move.invoice_line_ids:
									for line in move.invoice_line_ids:
										if line.tax_ids:
											final_discount = 0.0
											try:
												final_discount = ((move.discount_amount*line.price_subtotal)/amount_untaxed)
											except ZeroDivisionError:
												pass
											discount = line.price_subtotal 
											taxes = line.tax_ids.compute_all(discount, \
																move.currency_id,1.0, product=line.product_id, \
																partner=move.partner_id)
											sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
								move.update({
									'config_inv_tax': sums,
								})
							else:
								move.discount_amt_line = 0.00
								move_discount = amount_untaxed * (move.discount_amount / 100)

								res = move_discount
								if move.invoice_line_ids:
									for line in move.invoice_line_ids:
										if line.tax_ids:
											final_discount = 0.0
											try:
												final_discount = ((move.discount_amount*line.price_subtotal)/100.0)
											except ZeroDivisionError:
												pass
											discount = line.price_subtotal 
											taxes = line.tax_ids.compute_all(discount, \
																move.currency_id,1.0, product=line.product_id, \
																partner=move.partner_id)
											sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
						
								move.update({
									'config_inv_tax': sums,
								})
						else:

							if move.invoice_line_ids:
								for line in self.invoice_line_ids:
									if line.tax_ids:
										final_discount = 0.0
										try:
											test = move.invoice_line_ids.mapped('discount_method')
											if test == 'fix':
												final_discount = ((move.invoice_line_ids.discount_amount*line.price_subtotal)/amount_untaxed)
										except ZeroDivisionError:
											pass
										discount = line.price_subtotal

										taxes = line.tax_ids.compute_all(discount, \
															move.currency_id,1.0, product=line.product_id, \
															partner=move.partner_id)
										sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
			else:

				if res_config.tax_discount_policy == 'tax':
					if move.discount_method == 'fix':
						discount = move.discount_amount
						res = discount
					elif move.discount_method == 'per':
						total = 0.0
						tax = 0.0
						for line in self.invoice_line_ids:
							if line.exclude_from_invoice_tab == False:
								tax += line.com_tax()
								total += line.price_unit 

							res = (total + tax) * (move.discount_amount/ 100)
						   
					else:
						res = discount


					for line in move.invoice_line_ids:
						amount_untaxed += line.price_subtotal
						applied_discount += line.discount_amt
			
						if line.discount_method == 'fix':
							line_discount += line.discount_amount
							res = line_discount
						elif line.discount_method == 'per':
							# tax = line.com_tax()
							line_discount += line.price_subtotal  * (line.discount_amount/ 100)
							res = line_discount

				else:

					for line in move.invoice_line_ids:
						amount_untaxed += line.price_subtotal
						applied_discount += line.discount_amt
						res = applied_discount
			
						if line.discount_method == 'fix':
							line_discount += line.discount_amount
							res = line_discount
						elif line.discount_method == 'per':
							tax = line.com_tax()
							line_discount += (line.price_subtotal + tax) * (line.discount_amount/ 100)
							res = line_discount

					if move.discount_type == 'global':
						if move.discount_method == 'fix':
							move_discount = move.discount_amount
							res = move_discount
							if move.invoice_line_ids:
								for line in move.invoice_line_ids:
									if line.tax_ids:
										final_discount = 0.0
										try:
											final_discount = ((move.discount_amount*line.price_subtotal)/amount_untaxed)
										except ZeroDivisionError:
											pass
										discount = line.price_subtotal 
										taxes = line.tax_ids.compute_all(discount, \
															move.currency_id,1.0, product=line.product_id, \
															partner=move.partner_id)
										sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
							move.update({
								'config_inv_tax': sums,
							})
						else:
							move.discount_amt_line = 0.00
							move_discount = amount_untaxed * (move.discount_amount / 100)

							res = move_discount
							if move.invoice_line_ids:
								for line in move.invoice_line_ids:
									if line.tax_ids:
										final_discount = 0.0
										try:
											final_discount = ((move.discount_amount*line.price_subtotal)/100.0)
										except ZeroDivisionError:
											pass
										discount = line.price_subtotal 
										taxes = line.tax_ids.compute_all(discount, \
															move.currency_id,1.0, product=line.product_id, \
															partner=move.partner_id)
										sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
					
							move.update({
								'config_inv_tax': sums,
							})
					else:

						if move.invoice_line_ids:
							for line in self.invoice_line_ids:
								if line.tax_ids:
									final_discount = 0.0
									try:
										test = move.invoice_line_ids.mapped('discount_method')
										if test == 'fix':
											final_discount = ((move.invoice_line_ids.discount_amount*line.price_subtotal)/amount_untaxed)
									except ZeroDivisionError:
										pass
									discount = line.price_subtotal 

									taxes = line.tax_ids.compute_all(discount, \
														move.currency_id,1.0, product=line.product_id, \
														partner=move.partner_id)
									sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))            

		return res



	@api.depends(
		'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
		'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
		'line_ids.balance',
		'line_ids.currency_id',
		'line_ids.amount_currency',
		'line_ids.amount_residual',
		'line_ids.amount_residual_currency',
		'line_ids.payment_id.state',
		'line_ids.full_reconcile_id','discount_method','discount_amount','discount_amount_line')
	def _compute_amount(self):
		for move in self:
			total_untaxed, total_untaxed_currency = 0.0, 0.0
			total_tax, total_tax_currency = 0.0, 0.0
			total_residual, total_residual_currency = 0.0, 0.0
			total, total_currency = 0.0, 0.0

			for line in move.line_ids:
				if move.is_invoice(True):
					# === Invoices ===
					if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
						# Tax amount.
						total_tax += line.balance
						total_tax_currency += line.amount_currency
						total += line.balance
						total_currency += line.amount_currency
					elif line.display_type in ('product', 'rounding'):
						# Untaxed amount.
						total_untaxed += line.balance
						total_untaxed_currency += line.amount_currency
						total += line.balance
						total_currency += line.amount_currency
					elif line.display_type == 'payment_term':
						# Residual amount.
						total_residual += line.amount_residual
						total_residual_currency += line.amount_residual_currency
				else:
					# === Miscellaneous journal entry ===
					if line.debit:
						total += line.balance
						total_currency += line.amount_currency

			sign = move.direction_sign
			move.amount_untaxed = sign * total_untaxed_currency
			move.amount_tax = sign * total_tax_currency
			move.amount_total = sign * total_currency
			move.amount_residual = -sign * total_residual_currency
			move.amount_untaxed_signed = -total_untaxed
			move.amount_tax_signed = -total_tax
			move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
			move.amount_residual_signed = total_residual
			move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
			res = move._calculate_discount()
			move.discount_amt = res
			move.discount_amt_line = res
		   

	def _compute_amount_account(self):
		for record in self:
			for line in record.invoice_line_ids:
				if line.product_id:
					record.discount_account_id = line.account_id.id 
	

	@api.depends('discount_type')
	def _calculate_count_total(self):
		res_config= self.env.company
		final_count_total = 00
		for move in self :
			if self._context.get('default_move_type') in ['out_invoice', 'out_receipt', 'out_refund']:
				if move.discount_type == 'global':
					res = self._calculate_discount()
					if  move.config_inv_tax:
						move.update({
						   'count_total' : move.amount_untaxed + move.config_inv_tax,
						   'untax_test_amount' :  move.amount_untaxed,
						   'final_count_total' : move.amount_untaxed + move.config_inv_tax
						})
					else:
						test_amount =(move.amount_untaxed)
						move.update({
						   'count_total' : test_amount+ move.amount_tax,
						   'untax_test_amount' :  test_amount,
						   'final_count_total' : test_amount+ move.amount_tax,
						})
						
				else:
					res = self._calculate_discount()
					if  move.config_inv_tax:
						move.update({
						   'count_total' : move.amount_untaxed + move.config_inv_tax
						})
					else:
						test_amount =(move.amount_untaxed - res)
						move.update({
						   'count_total' : test_amount+ move.amount_tax,
						   'final_count_total': test_amount+ move.amount_tax,
						   'untax_test_amount' :  test_amount
						})
			else:
				res = self._calculate_discount()
				if move.discount_type == 'global':
					if  move.config_inv_tax:
						move.update({
						   'count_total' : move.amount_untaxed + move.config_inv_tax,
						   'untax_test_amount' :  move.amount_untaxed
						})
					else:
						# test_amount =(move.amount_untaxed - res)
						move.update({
						   'count_total' : move.amount_untaxed + move.amount_tax,
						   'untax_test_amount' :  move.amount_untaxed
						})
				else:
					if  move.config_inv_tax:
						move.update({
						   'count_total' : move.amount_untaxed + move.config_inv_tax
						})
					else:
						test_amount =(move.amount_untaxed - res)
						move.update({
						   'count_total' : test_amount+ move.amount_tax,
						   'untax_test_amount' :  test_amount
						})


	discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')],'Discount Method')
	discount_amount = fields.Float('Discount Amount')
	discount_amt = fields.Monetary(string='Discount', readonly=True, compute='_compute_amount')
	amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True,
		compute='_compute_amount')
	amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
		compute='_compute_amount')
	amount_total = fields.Monetary(string='Total', store=True, readonly=True,
		compute='_compute_amount',
		inverse='_inverse_amount_total')
	discount_type = fields.Selection([('line', 'Move Line'), ('global', 'Global')], 'Discount Applies to',default='global')
	discount_account_id = fields.Many2one('account.account', 'Discount Account',compute='_compute_amount_account',store=True)
	discount_amt_line = fields.Monetary(compute='_compute_amount', string='Line Discount', digits='Discount', store=True, readonly=True)
	discount_amount_line = fields.Monetary(string="Discount Line")
	config_inv_tax = fields.Monetary(string="total disc tax",compute="_calculate_discount",store=True)
	count_total = fields.Monetary(string="tax total",compute="_calculate_count_total",readonly=True)
	untax_test_amount = fields.Monetary(string="total untax amount for line",compute="_calculate_discount",store=True)
	final_count_total = fields.Monetary(string="total amount",compute="_calculate_discount",store=True)
   



	@api.depends('invoice_line_ids.tax_ids', 'invoice_line_ids.price_unit', 'amount_total', 'amount_untaxed','discount_amount','discount_amount_line')
	def _compute_tax_totals(self):

		res_config= self.env.company
		
		for move in self:
			if move.is_invoice(include_receipts=True):
				base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
				base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]

				if move.id:
					# The invoice is stored so we can add the early payment discount lines directly to reduce the
					# tax amount without touching the untaxed amount.
					sign = -1 if move.is_inbound(include_receipts=True) else 1
					base_line_values_list += [
						{
							**line._convert_to_tax_base_line_dict(),
							'handle_price_include': False,
							'quantity': 1.0,
							'price_unit': sign * line.amount_currency,
						}
						for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
					]

				kwargs = {
					'base_lines': base_line_values_list,
					'currency': move.currency_id,
				}

				if move.id:
					kwargs['tax_lines'] = [
						line._convert_to_tax_line_dict()
						for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
					]
				else:
					# In case the invoice isn't yet stored, the early payment discount lines are not there. Then,
					# we need to simulate them.
					epd_aggregated_values = {}
					for base_line in base_lines:
						if not base_line.epd_needed:
							continue
						for grouping_dict, values in base_line.epd_needed.items():
							epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
							epd_values['price_subtotal'] += values['price_subtotal']

					for grouping_dict, values in epd_aggregated_values.items():
						taxes = None
						if grouping_dict.get('tax_ids'):
							taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

						kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
							None,
							partner=move.partner_id,
							currency=move.currency_id,
							taxes=taxes,
							price_unit=values['price_subtotal'],
							quantity=1.0,
							account=self.env['account.account'].browse(grouping_dict['account_id']),
							analytic_distribution=values.get('analytic_distribution'),
							price_subtotal=values['price_subtotal'],
							is_refund=move.move_type in ('out_refund', 'in_refund'),
							handle_price_include=False,
						))
				tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)
				res = self._calculate_discount()

				if tax_totals.get('amount_untaxed'):
					tax_totals['amount_untaxed'] = tax_totals['amount_untaxed'] - res
					
				if tax_totals.get('formatted_amount_total'):
					if self.config_inv_tax :
						format_tax_total = tax_totals['amount_untaxed'] + self.config_inv_tax
					else:
						format_tax_total = tax_totals['amount_untaxed'] + move.amount_tax
					tax_totals['formatted_amount_total'] = formatLang(self.env, format_tax_total, currency_obj=self.currency_id)
				if tax_totals.get('formatted_amount_untaxed'):
					format_total = tax_totals['amount_untaxed']
					tax_totals['formatted_amount_untaxed'] = formatLang(self.env, format_total, currency_obj=self.currency_id)
                    
				

				groups_by_subtotal = tax_totals.get('groups_by_subtotal', {})
				if bool(groups_by_subtotal):
					_untax_amount = groups_by_subtotal.get('Untaxed Amount', [])
					if bool(_untax_amount):
						if res_config.tax_discount_policy == 'tax':
							for _tax in range(len(_untax_amount)):
								
								if _untax_amount[_tax].get('tax_group_base_amount'):
									tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
										'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - res 
									})
								if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
									format_total = _untax_amount[_tax]['tax_group_base_amount'] - res
									tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
										'formatted_tax_group_base_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
									})
						# else:
						# 	for _tax in range(len(_untax_amount)):
						# 		if  move.discount_type == 'global':
						# 			if _untax_amount[_tax].get('tax_group_amount'):
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'tax_group_amount' : self.config_inv_tax
						# 				})
										

						# 			if _untax_amount[_tax].get('tax_group_base_amount'):
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - res 
						# 				})
						# 			if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
						# 				format_total = _untax_amount[_tax]['tax_group_base_amount'] - res
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'formatted_tax_group_base_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
						# 				})

						# 			if _untax_amount[_tax].get('formatted_tax_group_amount'):
						# 				format_total = self.config_inv_tax
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'formatted_tax_group_amount' : formatLang(self.env, self.config_inv_tax, currency_obj=self.currency_id)
						# 				})
									
						# 		else:
						# 			if _untax_amount[_tax].get('tax_group_amount'):
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'tax_group_amount' : move.amount_tax
						# 				})

						# 			if _untax_amount[_tax].get('tax_group_base_amount'):
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'tax_group_base_amount' : _untax_amount[_tax]['tax_group_base_amount'] - res 
						# 				})
						# 			if _untax_amount[_tax].get('formatted_tax_group_base_amount'):
						# 				format_total = _untax_amount[_tax]['tax_group_base_amount'] - res
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'formatted_tax_group_base_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
						# 				})

						# 			if _untax_amount[_tax].get('formatted_tax_group_amount'):
						# 				format_total = move.amount_tax
						# 				tax_totals.get('groups_by_subtotal', {}).get('Untaxed Amount', [])[_tax].update({
						# 					'formatted_tax_group_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
						# 				})



				subtotals = tax_totals.get('subtotals', {})
				if bool(subtotals):
					for _tax in range(len(subtotals)):
						if subtotals[_tax].get('amount'):
							tax_totals.get('subtotals', {})[_tax].update({
								'amount' : subtotals[_tax]['amount'] - res
							})
						if subtotals[_tax].get('amount_tax'):
							tax_totals.get('subtotals', {})[_tax].update({
								'amount_tax' : res
							})
							

						if subtotals[_tax].get('formatted_amount'):
							format_total = subtotals[_tax]['amount']
							tax_totals.get('subtotals', {})[_tax].update({
								'formatted_amount' : formatLang(self.env, format_total, currency_obj=self.currency_id)
							})
					
				move.tax_totals = tax_totals
			else:
				# Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
				move.tax_totals = None

	@api.model_create_multi
	def create(self, vals_list):
		result = super(account_move,self).create(vals_list)
		if self._context.get('default_move_type') in ('out_invoice','out_refund','out_receipt'):
			for res in result:
				if res.discount_method and res.discount_amount:
					if res.state in 'draft':
						account = False
						for line in res.invoice_line_ids:
							if line.product_id:
								account = line.account_id.id    
						
						l = res.line_ids.filtered(lambda s: s.name == "Discount")
						
						if len(l or []) == 0 and account:
							discount_vals = {
								'account_id': account, 
								'quantity': 1,
								'price_unit': -res.discount_amt,
								'name': "Discount",
								'tax_ids' :None, 
								'exclude_from_invoice_tab': True,
								'display_type':'product',
								
								
							}
							res.with_context(check_move_validity=False).write({
									'invoice_line_ids' : [(0,0,discount_vals)]
								})
				else:
					if res.state in 'draft':
						account = False
						for line in res.invoice_line_ids:
							if line.product_id:
								account = line.account_id.id    
						
						l = res.line_ids.filtered(lambda s: s.name == "Discount")
						
						if len(l or []) == 0 and account:
							discount_vals = {
								'account_id': account, 
								'quantity': 1,
								'price_unit': -res.discount_amount_line,
								'name': "Discount",
								'tax_ids' :None, 
								'exclude_from_invoice_tab': True,
								'display_type':'product',
								'discount_amount': - res.discount_amount_line
								
								
							}
							res.with_context(check_move_validity=False).write({
									'invoice_line_ids' : [(0,0,discount_vals)]
								})
		else:
			for res in result:
				if res.invoice_line_ids:
					if res.invoice_line_ids[0].product_id:
						if "Down payment" in res.invoice_line_ids[0].product_id.name:
							res.write({'discount_method':'',
								'discount_amount':0})
				
				if res.discount_method and res.discount_amount:
					if res.state in 'draft':
						account = False
						for line in res.invoice_line_ids:
							if line.product_id:
								account = line.account_id.id    
						
						l = res.line_ids.filtered(lambda s: s.name == "Discount")
						
						if len(l or []) == 0 and account:
							discount_vals = {
								'account_id': account, 
								'quantity': 1,
								'price_unit': -res.discount_amt,
								'name': "Discount",
								'tax_ids' :None, 
								'exclude_from_invoice_tab': True,
								'display_type':'product',
								
								
							}
							res.with_context(check_move_validity=False).write({
									'invoice_line_ids' : [(0,0,discount_vals)]
								})
				else:
					if res.state in 'draft':
						account = False
						for line in res.invoice_line_ids:
							if line.product_id:
								account = line.account_id.id    
						
						l = res.line_ids.filtered(lambda s: s.name == "Discount")
						
						if len(l or []) == 0 and account:
							discount_vals = {
								'account_id': account, 
								'quantity': 1,
								'price_unit': -res.discount_amount_line,
								'name': "Discount",
								'tax_ids' :None, 
								'exclude_from_invoice_tab': True,
								'display_type':'product',
								'discount_amount': - res.discount_amount_line
								
								
							}
							res.with_context(check_move_validity=False).write({
									'invoice_line_ids' : [(0,0,discount_vals)]
								})

		return result                                    




class account_move_line(models.Model):
	_inherit = 'account.move.line'
 
	discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
	discount_type = fields.Selection(related='move_id.discount_type', string="Discount Applies to")
	discount_amount = fields.Float('Discount Amount')
	discount_amt = fields.Float('Discount Final Amount')
	flag = fields.Boolean("Flag")
	is_global_disc = fields.Boolean(string = "Global Discount")
	exclude_from_invoice_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")

	@api.depends('quantity','price','tax_ids','discount_amount')
	def com_tax(self):
		tax_total = 0.0
		tax = 0.0
		for line in self:
			for tax in line.tax_ids:
				tax_total += (tax.amount/100)*line.price_subtotal
			tax = tax_total
			return tax

	


