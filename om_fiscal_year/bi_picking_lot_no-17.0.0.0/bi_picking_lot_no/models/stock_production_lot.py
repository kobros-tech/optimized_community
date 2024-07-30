# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class stockProductionLot(models.Model):
    _inherit = 'stock.lot'

    name = fields.Char(default=False)

    def create_serial_no_stock(self):
        company = self.env.user.company_id
        result = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if result.apply_method == "global":
            digit = result.digits_lot_no
            prefix = result.prefix_lot_no
        else:
            digit = self.product_id.product_tmpl_id.digits_lot_no
            prefix = self.product_id.product_tmpl_id.prefix_lot_no
        lot_no = company.lot_no + 1
        lot_no_digit = len(str(lot_no))

        difference = abs(lot_no_digit - digit)
        if difference > 0:
            no = "0"
            for i in range(difference - 1):
                no = no + "0"
        else:
            no = ""

        if prefix:
            serial_no = prefix + no + str(lot_no)
        else:
            serial_no = str(lot_no)
        company.update({'lot_no': lot_no})
        return serial_no

    @api.onchange('product_id')
    def _onchange_product_id_auto_fill_lot(self):
        if self.product_id and self.product_id.tracking in ['serial', 'lot']:
            lot_serial_no_id = self.create_serial_no_stock()
            existing_line = self.search([('name', '=', lot_serial_no_id)])

            while existing_line:
                lot_serial_no_id = self.create_serial_no_stock()
                existing_line = self.search([('name', '=', lot_serial_no_id)])

            self.name = lot_serial_no_id