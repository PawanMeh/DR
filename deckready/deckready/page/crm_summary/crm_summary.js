frappe.pages["crm-summary"].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'CRM Summary',
		single_column: true
	});
	frappe.crmsummary = new frappe.CRMSummary(wrapper);
};

frappe.CRMSummary = Class.extend({
	init: function(wrapper) {
		this.page = wrapper.page;
		this.make();
	},
	make: function() {
		var me = this;

		me.page.add_field({
			fieldtype: "Date",
			fieldname: "from_date",
			label: __("From Date"),
			reqd: 1,
			default: frappe.datetime.get_today(),
			input_css: {"z-index": 1},
			change: function() {
				if (this && this.$input) {
					me.get_data();
				}
			}
		});

		me.page.add_field({
			fieldtype: "Date",
			fieldname: "to_date",
			label: __("To Date"),
			reqd: 1,
			default: frappe.datetime.get_today(),
			input_css: {"z-index": 1},
			change: function() {
				if (this && this.$input) {
					me.get_data();
				}
			}
		});	

		me.page.add_field({
			fieldtype: "Link",
			fieldname: "campaign_name",
			label: __("Campaign"),
			reqd: 1,
			default: "Canvas",
			options:"Campaign",
			input_css: {"z-index": 1},
			change: function() {
				if (this && this.$input) {
					me.get_data();
				}
			}
		});

		me.get_data()	
	},
	get_data: function() {
		var me = this;
		frappe.call({
			method: "deckready.deckready.page.crm_summary.crm_summary.get_crm_summary_data",
			args: {
				"from_date": me.page.fields_dict["from_date"].get_value(),
				"to_date": me.page.fields_dict["to_date"].get_value(),
				"campaign_name": me.page.fields_dict["campaign_name"].get_value()
			}
		}).done((r) => {
			me.page.wrapper.find('.crm-summary').remove()
			me.page.main.append(r.message)
		}).fail((reason) => {
			//frappe.show_alert("Could not load data. <br/>" + reason);
			frappe.show_alert("Data not found for the criteria entered.");
		})
	}
})

