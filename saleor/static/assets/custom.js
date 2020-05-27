$(document).ready(function() {
    "use strict";
    $('body').on('input', 'input[type="number"]', function(){
        var x = parseFloat(this.value);
        var y = parseFloat($(this).parent().parent().parent().find('.unitprice').val());
        $(this).parent().parent().parent().find('.amount_price').val((x * y).toFixed(3));
    });
    
    $('body').on('input', 'input.unitprice', function(){
        var x = parseFloat(this.value);
        var y = parseFloat($(this).parent().parent().parent().find('input[type="number"]').val());
        $(this).parent().parent().find('.amount_price').val((x * y).toFixed(3));
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

