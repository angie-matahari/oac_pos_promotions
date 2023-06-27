odoo.define('pos_promotion.models', function (require) {

    var models = require('point_of_sale.models');

    models.load_fields("pos.order.line", ['pos_promotion_item_id']);

    models.PosModel.prototype.models.push({
        model:  'pos.promotion',
        fields: [],
        domain: function(self){
            var current_date = moment(new Date()).locale('en').format("YYYY-MM-DD");
            return [['from_date', '<=', current_date], ['to_date', '>=', current_date], ['state', '=', 'in_progress']];
        },
        loaded: function(self, pos_promotions){
            self.pos_promotions = pos_promotions;
            self.promotions_by_id = {};
            _.each(promotions, function(promotion){
                self.promotions_by_id[promotion.id] = promotion;
            })
        },
    },
    {
        model:  'pos.promotion.item',
        fields: [],
        domain: function(self){
            var current_date = moment(new Date()).locale('en').format("YYYY-MM-DD");
            return [['from_date', '<=', current_date], ['to_date', '>=', current_date], ['state', '=', 'in_progress']];
        },
        loaded: function(self, pos_promotion_items){
            self.pos_promotion_items_by_product_id = {};
            self.pos_promotion_items = pos_promotion_items;
            _.each(pos_promotion_items, function(promomotion_item){
                if (!(promomotion_item.promotion_product_id.id in self.pos_promotion_items_by_product_id)){
                    self.pos_promotion_items_by_product_id[promomotion_item.promotion_product_id.id] = []
                }
                self.pos_promotion_items_by_id[promomotion_item.id].push(promomotion_item);
            })
        },
    });

    const SuperOrder = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            SuperOrder.add_product.apply(this, arguments);
            this.apply_pos_promotion(product);
        },
        apply_pos_promotion: function(product){
            var selected_line =  this.get_selected_orderline();
            var promotion_item = this.pos_promotion_items_by_product_id[product.id] && this.pos_promotion_items_by_product_id[product.id][0];

            if (promotion_item){
                selected_line.set_promotion_item(promotion_item);
                selected_line.set_unit_price(promotion_item.promotion_price)
            }
        }
    });

    var SuperOrderLine = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options){
            SuperOrderLine.initialize.call(this, attr, options);
            this.pos_promotion_item_id = this.pos_promotion_item_id || false;
            this.promotion_code = this.promotion_code || false;
        },
        export_as_JSON: function(){
            const json = SuperOrder.export_as_JSON.call(this);
            json.pos_promotion_item_id = this.pos_promotion_item_id;
            json.promotion_code = this.promotion_code;
            return json;
        },
        init_from_JSON: function(json){
            SuperOrder.init_from_JSON.apply(this, arguments);
            this.pos_promotion_item_id = json.pos_promotion_item_id;
            this.promotion_code = json.promotion_code;
        },
        set_promotion_item: function(promotion_item){
            this.pos_promotion_item_id = promotion_item.id;
            this.promotion_code = promotion_item.promotion_id.name;
        },
        get_promotion_code: function(){
            return this.promotion_code;
        }

    });
});