# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    pos_promotion_item_id = fields.Many2one('pos.promotion.item', string='POS Promotion Item')
    promotion_id = fields.Many2one('pos.promotion', related='pos_promotion_item_id.promotion_id',
                                   string='POS Promotion', store=True)
