$(document).ready(function() {
    "use strict";
    $('body').on('input', 'input[type="number"]', function(){
        var x = parseFloat(this.value);
        var y = parseFloat($(this).parent().parent().parent().find('.unitprice').text());
        $(this).parent().parent().parent().find('.amount_price').text(x * y);
    });
});

function myFunction(x) {
    x.classList.toggle("fa-thumbs-down");
    if($(x).find('.status_val').val() == "Accept")
    {
        $(x).find('.status_val').val("Deny");
    }
    else{
        $(x).find('.status_val').val("Accept");
    }
    console.log($(x).find('.status_val').val());
}

