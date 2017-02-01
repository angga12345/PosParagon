odoo.define('pti_pos_free_product.loyalty', function (require) {
 "use strict";
 
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');

var _super_posloyalty = models.Order;
models.Order = models.Order.extend({
	
	set_gift_reward: function(line, gift_product){
		line.reward_gift_id = gift_product.id;
	},

	get_available_rewards_automatic: function(){
		return _super_posloyalty.prototype.get_available_rewards_automatic.apply(this, arguments)
	},
	
	apply_reward: function(reward){
		var client = this.get_client();
        var product, order_total, spendable;
        var lrounding, crounding;
        var list_price=[]
        var products=[]
        var rules = this.pos.loyalty.rules;
        var lines = this.get_orderlines();
        var active_rules = this.get_rules_active_id();
        var product_ids = []
        var category_ids = []
	    for(var i = 0;i < active_rules.length; i++){
        	console.log(active_rules[i].product_ids + '+++++++++++====')
        	if (active_rules[i].product_ids){
	        	for(var j = 0;j < active_rules[i].product_ids.length; j++){
	            	product_ids.push(active_rules[i].product_ids[j])
	        	}
	        }else if(active_rules[i].category_selected){
	        	for(var j = 0;j < active_rules[i].category_selected.length; j++){
	            	category_ids.push(active_rules[i].category_selected[j])
	        	}
	        	console.log(category_ids)
	        }
	    }
        console.log('Rules',rules, reward, this.pos.loyalty)
//        if(rules.is_cheapest_product){
        var prod_cheapest=[]
        var prod_rules=[]
        var prod_rules_categ=[]
        var prod_rules_price=[]

        if (reward.type === 'discount' && reward.is_cheapest_product){
        	var rule_id = this.pos.loyalty.rewards;
        	var rule_now;
        	var sum_prod_rules=0;
        	console.log('rules if reward discount and cheapest',rules)
        	
        	for (i in rules){
        		if (rules[i].type=='product'){
            		console.log('rules[i] reward.rule_id[1]',rules[i].name,reward.rule_id[1])
            		if (rules[i].name==reward.rule_id[1]){
            			rule_now = rules[i];
            			for (var j in rules[i].product_ids){
            				prod_rules.push(rules[i].product_ids[j])
            				console.log('prod rules id', rules[i].product_ids[j])
            			}
            		}
	            	console.log('prod rules',prod_rules)
	            	lines = this.get_orderlines();
	            	console.log('min obj',this.get_orderlines())
	            	console.log('lines',lines)
	            	
	            	for (var i in lines){
	            		for (var j in prod_rules){
	            			if(prod_rules[j] == lines[i].product.id){
	            				sum_prod_rules = sum_prod_rules + lines[i].quantity
	            				console.log('sum',sum_prod_rules)
	            			}
	            		}
	            	}
	            }
        		else if (rules[i].type=='category'){
            		console.log('rules[i] category reward.rule_id[1]',rules[i].name,reward.rule_id[1])
            		if (rules[i].name==reward.rule_id[1]){
            			rule_now = rules[i];
            			for (var j in rules[i].category_ids){
            				prod_rules_categ.push(rules[i].category_ids[j])
            				console.log('categ rules id', rules[i].category_ids[j])
            			}
            		}
	            	console.log('prod rules categ',prod_rules_categ)
	            	lines = this.get_orderlines();
	            	console.log('min obj',this.get_orderlines())
	            	console.log('lines',lines)
	            	
	            	for (var i in lines){
	            		for (var j in prod_rules_categ){
	            			for (var k in lines[i].product.category_ids){
	            				console.log('prod categ ids k',lines[i].product.category_ids[k])
	            				if(prod_rules_categ[j] == lines[i].product.category_ids[k]){
	            					sum_prod_rules = sum_prod_rules + lines[i].quantity
	            					prod_rules.push(lines[i].product.id)
		            				console.log('sum',sum_prod_rules)
	            				}
	            			}
	            		}
	            	}
	            	console.log('prod rules', prod_rules)
	            }
        	}
        	
        	
        	
        	console.log('rule_now',rule_now,sum_prod_rules)
        	if (sum_prod_rules >= rule_now.qty_rule){
	        	var tmp1, min_prod, min_line, line;
	        	var lowest1 = Number.POSITIVE_INFINITY;
	        	for (var i = lines.length-1; i>=0; i--) {
	        		for (var k in prod_rules){
	        			console.log('rules[k] lines[i].id',prod_rules[k],lines[i].product.id)
	        			if(prod_rules[k] == lines[i].product.id){
	        				line = lines[i];
	                		tmp1 = line.price
	            			if (tmp1 < lowest1){
	            				lowest1 = tmp1
	            				min_line=line
	            				console.log('min_line',min_line)
	            			}
	        			}
	        		}
	    			
	    		}
	        	if (min_line.quantity == 1){
	        		for (var i = 0; i < lines.length; i++) {
	        			var line = lines[i];
	        			if(active_rules.length){
	    	    			for (var j=0; j < product_ids.length; j++){
	    	    				if(line.product.id == product_ids[j]){
	    	    					line.reward_id = reward.id;
	    	    				}
	    	    			}
	        			}else{
	        				line.reward_id = reward.id;
	        			}
	                }
	        		this.select_orderline(min_line);
	            	this.selected_orderline.set_discount(100);
	            	this.selected_orderline.reward_id = reward.id;
	            	console.log('min_lines',min_line, this.selected_orderline)
	        	}
	        	else if (min_line.quantity > 1){
	        		this.select_orderline(min_line);
	        		this.selected_orderline.set_quantity(min_line.quantity - 1);
	        		product=this.pos.db.get_product_by_id(this.selected_orderline.product.id);
	        		for (var i = 0; i < lines.length; i++) {
	        			var line = lines[i];
	        			if(active_rules.length){
	    	    			for (var j=0; j < product_ids.length; j++){
	    	    				if(line.product.id == product_ids[j]){
	    	    					line.reward_id = reward.id;
	    	    					this.set_gift_reward(line, product)
	    	    				}
	    	    			}
	        			}else{
	        				line.reward_id = reward.id;
	        				this.set_gift_reward(line, product)
	        			}
	                }
	        		this.add_product(product, { 
	                  price: 0, 
	                  quantity: 1, 
	                  discount: 100,
	                  merge: false, 
	                  extras: { reward_id: reward.id }
	        		});
	        	}
        	}
        }
    	
    	
        else if (reward.type === 'gift') {
            product = this.pos.db.get_product_by_id(reward.gift_product_id[0]);
            
            if (!product) {
                return;
            }
            for (var i = 0; i < lines.length; i++) {
    			var line = lines[i];
    			if(active_rules.length){
	    			for (var j=0; j < product_ids.length; j++){
	    				if(line.product.id == product_ids[j]){
	    					line.reward_id = reward.id;
	    		        	this.set_gift_reward(line, product);
	    				}
	    			}
    			}else{
    				line.reward_id = reward.id;
    				this.set_gift_reward(line, product);
    			}
            }
            this.add_product(product, { 
                price: 0, 
                discount: 100,
                quantity: 1, 
                merge: false, 
//                extras: { reward_id: reward.id },
            });

        } else if (reward.type === 'discount' && !reward.is_cheapest_product) {
            if(reward.is_multilevel_discount){
            	var product = this.pos.db.get_product_by_id(reward.discount_product_id[0]);

            	if(!product){
            		return;
            	}
            	for (var i = 0; i < lines.length; i++) {
        			var line = lines[i];
        			if(active_rules.length){
    	    			for (var j=0; j < product_ids.length; j++){
    	    				if(line.product.id == product_ids[j]){
    	    					line.reward_id = reward.id;
    	    				}
    	    			}
        			}else{
        				line.reward_id = reward.id;
        			}
                }
            	var display_name = product.display_name
            	product.display_name = display_name + ' - ' + reward.name;

            	this.add_product(product, {
            		quantity: 1, 
            		merge: false,
//            		extras: { reward_id: reward.id },
            	});
        	}
            else if(!reward.is_multilevel_discount && reward.is_for_all){
        		var lines = this.get_orderlines();
        		for (var i = 0; i < lines.length; i++) {
        			var line = lines[i];
        			if (reward.discount > line.discount_base){
        				if(active_rules.length){
    		    			for (var j=0; j < product_ids.length; j++){
    		    				if(line.product.id == product_ids[j]){
    		    					line.reward_id = reward.id;
    		    				}
    		    			}
    	    			}else{
    	    				line.reward_id = reward.id;
    	    			}
    					line.discountStr = '' + reward.discount;
    					line.discount_base = reward.discount;
    					line.trigger('change', line);
        			}
					this.select_orderline(line);
				}

            }
        	else{
        		var lines = this.get_orderlines();
        		var total = 0
        		for (var i = 0; i < lines.length; i++) {
        			var line = lines[i];
        			if (reward.triggerby_active_rules){
	        			for (var obj in reward.triggerby_active_rules){
	        				var rule = reward.triggerby_active_rules[obj];
	        				console.log('rule rule',rule)
        					if (rule.count_product > 0 && rule.product_selected.length == rule.count_product){
        						console.log('pppppppppppppppppppppp')
        						for (var ps in rule.product_selected){
        							var product = rule.product_selected[ps];
        							if(line.get_product().id == product){
        								for (var i = 0; i < lines.length; i++) {
        					    			var line = lines[i];
        					    			if(active_rules.length){
        						    			for (var j=0; j < product_ids.length; j++){
        						    				if(line.product.id == product_ids[j]){
        						    					line.reward_id = reward.id;
        						    				}
        						    			}
        					    			}else{
        					    				line.reward_id = reward.id;
        					    			}
        					            }
        								var disc_value = line.get_display_price() * (reward.discount/100);
        	        					line.discountStr = '' + reward.discount;
        	        					line.discount_base = reward.discount;
        	        					line.trigger('change', line);
        	        					line['got_reward'] = reward;
        	        					this.select_orderline(line);	
        							}
        						}
	        				}else if(category_ids){
	        					var product_category_ids = line.get_product().category_ids;
	        					for(var i=0; i<product_category_ids.length;i++){
	        						for(var j=0;j<category_ids.length;j++){
	        							lines = this.get_orderlines();
	        							for(var l in lines){
	        								var l2 = lines[l];
//	        								var disc_value = l2.get_display_price() * (reward.discount/100);
	        	        					l2.discountStr = '' + reward.discount;
	        	        					l2.discount_base = reward.discount;
	        	        					l2['got_reward'] = reward;
	        	        					l2.trigger('change', l2);
	        	        					this.select_orderline(l2);
	        	        	            	this.selected_orderline.reward_id = reward.id;
	        							}
	        						}
	        					}
	        				}
	        			}
        			}else{
        				if(product_ids){
        					lines = this.get_orderlines();
        					for(var l in lines){
								var l2 = lines[l];
								if ($.inArray(line.get_product().id, product_ids) > -1 ){
//									var disc_value = l2.get_display_price() * (reward.discount/100);
		        					l2.discountStr = '' + reward.discount;
		        					l2.discount_base = reward.discount;
		        					l2['got_reward'] = reward;
		        					l2.trigger('change', l2);
		        					this.select_orderline(l2);
		        	            	this.selected_orderline.reward_id = reward.id;
								}
							}
        				}
        				var tot_tax = this.get_total_tax();
        				var active_rules = this.get_rules_active_id();
        				var ln_product_id = line.get_product().id;
        				var ln_product = line.get_product();
        				//console.log('get product',line)
        				for (var a in active_rules){
        					if(active_rules[a].price_rule > 0){
        						console.log('Price rule: ',active_rules[a])
        						if(active_rules[a].produk_pwp_ids){
        							//active rules produk pwp ids
        							for (var b in active_rules[a].produk_pwp_ids){
                						var list_prod_pwp = active_rules[a].produk_pwp_ids[b];
                						if(ln_product_id == list_prod_pwp){
                							//console.log('produk pwp')
                							////console.log('produk',ln_product)
                							var ln_prc = ln_product.price * line.quantity;
                							////console.log('lol',ln_prc, total)
                	        				total = total + ln_prc;
                	        				break;
                						}
                						
                					}
        						}else{
        							//active rules product ids
        							for (var b in active_rules[a].product_ids){
                						var list_prod_pwp = active_rules[a].product_ids[b];
                						if(ln_product_id == list_prod_pwp){
                							////console.log('produk pwp')
                							////console.log('produk',ln_product)
                							var ln_prc = ln_product.price * line.quantity;
                							////console.log('lol',ln_prc, total)
                	        				total = total + ln_prc;
                	        				break;
                						}
                						
                					}
        						}
        						
        						
        					break;	
        					}
        				}
        				
        				//console.log('Total sekarang: ',total)
    					// untuk PWP
        				if (total > active_rules[a].price_rule){
        					/*Menambahkan Product Discount DiAwal,DiTengah*/
        					for(var line_prod in lines){
    							if(lines[line_prod].product.id == reward.discount_product_id[0]){
    								//adjustment amount of products
    								var disc_value = lines[line_prod].price * (reward.discount/100);
    								lines[line_prod].discountStr = '' + reward.discount;
    								lines[line_prod].discount_base = reward.discount;
    								line.trigger('change', line);
    								this.select_orderline(lines[line_prod]); // menyisipkan langsung diskon ke produk
    								
    							}
    							
    						}
        					/**/
        					
        					/*menambahkan Product Discount DiAkhir*/
        					if (line.get_product().id == reward.discount_product_id[0]){
        						for (var i = 0; i < lines.length; i++) {
        			    			var line = lines[i];
        			    			if(active_rules.length){
        				    			for (var j=0; j < product_ids.length; j++){
        				    				if(line.product.id == product_ids[j]){
        				    					line.reward_id = reward.id;
        				    				}
        				    			}
        			    			}else{
        			    				line.reward_id = reward.id;
        			    			}
        			            }
        						var disc_value = line.get_display_price() * (reward.discount/100);
	        					line.discountStr = '' + reward.discount;
	        					line.discount_base = reward.discount;
	        					line.trigger('change', line);
	        				}
        					/**/
        					this.select_orderline(line); // menyisipkan langsung diskon ke produk
    						
        				}
        				
        			}
        		}
        	}

        } else if (reward.type === 'resale') {
            lrounding = this.pos.loyalty.rounding;
            crounding = this.pos.currency.rounding;
            spendable = this.get_spendable_points();
            order_total = this.get_total_with_tax();
            product = this.pos.db.get_product_by_id(reward.point_product_id[0]);

            if (!product) {
                return;
            }

            if ( round_pr( spendable * product.price, crounding ) > order_total ) {
                spendable = round_pr( Math.floor(order_total / product.price), lrounding);
            }

            if ( spendable < 0.00001 ) {
                return;
            }

            this.add_product(product, {
                quantity: -spendable,
                merge: false,
                extras: { reward_id: reward.id },
            });
        }
        
    },
});

})