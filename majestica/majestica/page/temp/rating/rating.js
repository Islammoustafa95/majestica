frappe.pages['feedback'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Thanks For Choosing Us',
		single_column: true
	});
	page.main.html(frappe.render_template("feedback", { 'doc': "" }));
	$("[name='quality_of_cleanliness']").change(function () {
		$("[name='quality_of_cleanliness']").parent().css("background", "none");
		if ($(this).is(":checked")) {
			$(this).parent().css("background", "rgb(199, 199, 242, 0.5)");
		}
	});

	$("[name='quality_of_products']").change(function () {
		$("[name='quality_of_products']").parent().css("background", "none");
		if ($(this).is(":checked")) {
			$(this).parent().css("background", "rgb(199, 199, 242, 0.5)");
		}
	});

	$("[name='quality_of_service']").change(function () {
		$("[name='quality_of_service']").parent().css("background", "none");
		if ($(this).is(":checked")) {
			$(this).parent().css("background", "rgb(199, 199, 242, 0.5)");
		}
	});
	page.main.find("#fback").on("submit", function (event) {
		event.preventDefault();
		console.log($(this).serialize());
		console.log($(this).serializeJSON())
		// frappe.call({
		// 	"method": "majestica.whitelisted.save_rating",
		// 	"args": {
		// 		"customer": document.getElementById("cust").innerHTML,
		// 		"invoice": document.getElementById("invoice").innerHTML,
		// 		"quality_of_service": quality_of_service,
		// 		"quality_of_products": quality_of_products,
		// 		"quality_of_cleanliness": quality_of_cleanliness
		// 	}
		// });
	});

}

