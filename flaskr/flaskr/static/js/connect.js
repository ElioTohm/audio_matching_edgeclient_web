document.getElementById("Connect").className = "active";
document.getElementById("Status").className = "";

$('.btn .btn-success').click(function () {
	alert();
	$('#SSID').val() = $(this).attr('id');
});