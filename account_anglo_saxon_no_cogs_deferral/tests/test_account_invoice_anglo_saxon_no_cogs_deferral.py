# Copyright 2015-2018 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountAngloSaxonNoCogsDeferral(TransactionCase):

    def setUp(self):
        super(TestAccountAngloSaxonNoCogsDeferral, self).setUp()

        # ENVIRONEMENTS
        self.Invoice = self.env['account.invoice']
        self.Account = self.env['account.account']
        # INSTANCES
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.customer_location = self.env.ref(
            'stock.stock_location_customers')
        self.supplier_location = self.env.ref(
            'stock.stock_location_suppliers')
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner'
        })
        self.product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product1.product_tmpl_id.valuation = 'real_time'
        self.product1.product_tmpl_id.cost_method = 'real'
        self.stock_input_account = self.Account.create({
            'name': 'Stock Input',
            'code': 'StockIn',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_liabilities').id,
        })
        self.stock_output_account = self.Account.create({
            'name': 'COGS',
            'code': 'cogs',
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id,
        })
        self.stock_valuation_account = self.Account.create({
            'name': 'Stock Valuation',
            'code': 'Stock Valuation',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
        })
        self.stock_journal = self.env['account.journal'].create({
            'name': 'Stock Journal',
            'code': 'STJTEST',
            'type': 'general',
        })
        self.product1.categ_id.write({
            'property_stock_account_input_categ_id':
                self.stock_input_account.id,
            'property_stock_account_output_categ_id':
                self.stock_output_account.id,
            'property_stock_valuation_account_id':
                self.stock_valuation_account.id,
            'property_stock_journal': self.stock_journal.id,
        })

    def create_invoice(self):
        receivable = self.env.ref('account.data_account_type_receivable').id
        return self.env['account.invoice'].create({
            'partner_id': self.partner.id,
            'name': "Test",
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product1.id,
                    'name': self.product1.name,
                    'account_id': self.env['account.account'].search(
                        [('user_type_id', '=', receivable)], limit=1).id,
                    'quantity': 10.0,
                    'price_unit': 10.0,
                })
            ]
        })

    def test_create_invoice(self):
        pick = self.env['stock.picking'].create({
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
        })
        # receive 10 units @ 10.00 per unit
        move1 = self.env['stock.move'].create({
            'name': 'IN 10 units @ 10.00 per unit',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'picking_id': pick.id,
            'product_uom_qty': 10.0,
            'price_unit': 10.0,
        })
        move1.action_confirm()
        move1.action_assign()
        move1.qty_done = 10.0
        pick.force_assign()
        pick.move_lines.write({'quantity_done': 1})
        pick.action_done()
        self.assertEqual(pick.state, 'done')
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        # Check that there's no cogs line involved in the customer invoice
        cogs_line = invoice.move_id.mapped('line_ids').filtered(
            lambda l: l.account_id.code == 'cogs')
        self.assertEqual(len(cogs_line), 0)
        # Check that the account move originating from the stock move has a
        # COGS account.
        move = self.env['account.move'].search([('ref', '=', pick.name)])
        self.assertEquals(len(move), 1)
        cogs_line = move.mapped('line_ids').filtered(
            lambda l: l.account_id.code == 'cogs')
        self.assertEqual(len(cogs_line), 1)
