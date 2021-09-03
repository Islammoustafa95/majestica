frappe.pages['rating'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Thanks For Choosing Us',
		single_column: true
	});
	page.main.html(frappe.render_template("rating", { 'doc': "" }));
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
	$("[name='age-group']").change(function () {
		$("[name='age-group']").parent().css("background", "none");
		$(".age-g").attr("src", "/files/correct1.png")
		if ($(this).is(":checked")) {
			console.log('check')
			$(this).parent().find("img").remove();
			$(this).parent().append("<img class='age-g' src='/files/correct2.png'></img>")
		}
		else {
			console.log('uncheck')
			$(this).parent().find("img").remove();
			$(this).parent().append("<img class='age-g' src='/files/correct1.png'></img>")
		}
	});
	page.main.find("#fback").on("submit", function (event) {
		event.preventDefault();
		console.log($(this).serialize());
		var data = $(this).serialize().split("&")
		frappe.call({
			"method": "majestica.whitelisted.save_rating",
			"args": {
				"customer": localStorage.getItem("customer"),
				"invoice": localStorage.getItem("invoice"),
				"quality_of_service": data[0].split("=")[1],
				"quality_of_products": data[1].split("=")[1],
				"quality_of_cleanliness": data[2].split("=")[1],
				"age_group":data[3].split("=")[1],
			}
		});
		window.location.replace("http://119.160.129.5/desk#point-of-sale");
	});

}

