// Copyright (c) 2016, hello@openetech.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Campaign Category Analysis"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_default("year_start_date"),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"campaign_sub_category",
			"label": __("Campaign Sub Category"),
			"fieldtype": "Check"
		},
		{
			"fieldname":"campaign_name",
			"label": __("Campaign Name"),
			"fieldtype": "Link",
			"options": "Campaign"
		}
	]
}