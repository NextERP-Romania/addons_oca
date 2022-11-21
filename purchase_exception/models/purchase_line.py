# Copyright 2017 Akretion (http://www.akretion.com)
# Copyright 2020 Camptocamp SA
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import html


class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line", "base.exception.method"]
    _name = "purchase.order.line"

    ignore_exception = fields.Boolean(
        related="order_id.ignore_exception", store=True, string="Ignore Exceptions"
    )
    exception_ids = fields.Many2many(
        "exception.rule", string="Exceptions", copy=False, readonly=True
    )
    exceptions_summary = fields.Html(
        readonly=True, compute="_compute_exceptions_summary"
    )

    @api.depends("exception_ids", "ignore_exception")
    def _compute_exceptions_summary(self):
        for rec in self:
            if rec.exception_ids and not rec.ignore_exception:
                rec.exceptions_summary = rec._get_exception_summary()
            else:
                rec.exceptions_summary = False

    def _get_exception_summary(self):
        return "<ul>%s</ul>" % "".join(
            [
                "<li>%s: <i>%s</i></li>"
                % tuple(map(html.escape, (e.name, e.description)))
                for e in self.exception_ids
            ]
        )

    def _get_main_records(self):
        return self.mapped("order_id")

    @api.model
    def _reverse_field(self):
        return "purchase_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        # Thanks to the new flush of odoo 13.0, queries will be optimized
        # together at the end even if we update the exception_ids many times.
        # On previous versions, this could be unoptimized.
        (self - records).exception_ids = [(3, rule.id)]
        records.exception_ids = [(4, rule.id)]
        return records.mapped("order_id")
