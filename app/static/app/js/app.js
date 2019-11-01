
$('#myform').on('sumbit', function (e) {
    e.preventDefault();
})


$('.save').on('click', function (e) {
    $('.save').addClass('disabled');
    $('#myform').submit();
})

conditions = $('#filter').serializeArray();
$.each(conditions, function () {
    if (this.value) {
        $('.filtered').css('visibility', 'visible')
    }
})

$(".pagination").rPage();