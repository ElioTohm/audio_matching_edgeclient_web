document.getElementById("Connect").className = "active";
document.getElementById("Status").className = "";
document.getElementById("Register").className = "";

$('.btn-success').on( 'click',function () {
	$('#SSID').val($(this).attr('id'));
});