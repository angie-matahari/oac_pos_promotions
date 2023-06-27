# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PosPromotions(models.Model):
    _name = 'pos.promotion'
    _rec_name = 'name'
    _description = 'POS Promotions'
    _inherit = 'mail.thread'

    _sql_constraints = [
        ('unique_promotion_code', 'unique (name)', 'The Promotion Code must be unique!'),
        ('from_to_dates_check', 'CHECK(from_date <= to_date)', 'The Promotion Code must be unique!')
    ]

    name = fields.Char('Promotion Code', required=True, copy=False, default='New Promo', tracking=True)
    from_date = fields.Date('From', required=True, tracking=True)
    to_date = fields.Date('To', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('ended', 'Promotion Ended'),
        ('cancel', 'Canceleld')
    ], string='Status', default='draft', tracking=True)
    promotion_item_ids = fields.One2many('pos.promotion.item', 'promotion_id', string='Promotion Items', tracking=True)
    pos_order_line_ids = fields.One2many('pos.order.line', 'promotion_id', string='POS Orders')
    pos_order_count = fields.Integer(compute='_compute_pos_order_count', string='Pos Order Count', store=True)

    @api.constrains('from_date')
    def _constrains_from_date(self):
        for promotion in self:
            if promotion.from_date < date.today():
                raise ValidationError(_("The Promotion start date cannot start before today."))

    def unlink(self):
        for promotion in self:
            if promotion.state in ('in_progress', 'confirm'):
                raise UserError(_("You cannot delete a promotion in progress. Please cancel it and try again."))
        return super(PosPromotions, self).unlink()

    @api.depends('pos_order_ids')
    def _compute_pos_order_count(self):
        for promotion in self:
            promotion.pos_order_count = len(promotion.pos_order_line_ids)

    def button_start(self):
        self.ensure_one()
        values = {'state': 'in_progress'}
        if self.from_date > date.today():
            values['from_date'] = date.today()
        self.write({'state': 'in_progress'})
        return {}

    def button_draft(self):
        if self.state != 'cancel':
            raise UserError(_("Promotion cannot be rest to draft unless in 'Cancelled' status"))
        self.write({'state': 'draft', 'from_date': date.today(), 'to_date': date.today()})
        return {}

    def button_confirm(self):
        self.write({'state': 'confirm'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_end(self):
        self.ensure_one()
        self.write({'state': 'ended', 'to_date': date.today()})

    def action_view_pos_order_lines(self):
        self.ensure_one()
        return {
            'name': _('Promotion Sales'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'pos.order.line',
            'domain': [('id', 'in', self.pos_order_line_ids.ids)]
        }

    def cron_start_promotion(self):
        self = self.filtered(lambda promo: promo.state == 'confirm' and promo.from_date == date.today())
        for promotion in self:
            promotion.button_start()

    def cron_end_promotion(self):
        self = self.filtered(lambda promo: promo.state == 'in_progress' and promo.to_date <= date.today())
        for promotion in self:
            promotion.button_end()


class PosPromotionItems(models.Model):
    _name = 'pos.promotion.item'
    _rec_name = 'product_id'
    _description = 'POS Promotion Items'

    _sql_constraints = [
        ('promotion_price_check', 'CHECK(promotion_price > 0)', 'The Promotion Price must be greater than zero!')
    ]

    promotion_product_id = fields.Many2one('product.product', string='Promotion Product', required=True, tracking=True)
    promotion_price = fields.Float('Promotion Price', required=True, tracking=True)
    promotion_id = fields.Many2one('pos.promotion', string='POS Promotion', required=True)
    from_date = fields.Date('From', required=True, related='promotion_id.from_date', store=True)
    to_date = fields.Date('To', required=True, related='promotion_id.from_date', store=True)
    state = fields.Selection('Status', required=True, related='promotion_id.state', store=True)
