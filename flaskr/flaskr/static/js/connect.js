document.getElementById("Connect").className = "active";
document.getElementById("Status").className = "";

$('.btn-success').on( 'click',function () {
	$('#SSID').val($(this).attr('id'));
});