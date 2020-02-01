function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');    function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        console.log('ALSO RUNNING')
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$( ".approve-dish" ).on( "click", function() {
    var url = $(this).prev().attr('href');
    var dishId = extractDishId(url)
    var slug = extractSlug(window.location.href)

    $.ajax({

        url : 'http://localhost:8000/approve_dish/',
        type : 'POST',
        data : {
            'dishId': dishId,
            'slug': slug,
        },
        success : function(data) {
            console.log('Success', data.dishId)
            $("#" + "approve_" +  dishId).children().css('opacity', 0.3)
        },
        error : function(request,error)
        {
            console.log(error)
        }
    });
});

$( ".cancel-dish" ).on( "click", function() {

    var url = $(this).prev().prev().attr('href');
    var dishId = extractDishId(url)
    var slug = extractSlug(window.location.href)

    $.ajax({

        url : 'http://localhost:8000/cancel_dish/',
        type : 'POST',
        data : {
            'dishId': dishId,
            'slug': slug,
        },
        success : function(data) {
            $("#" + "cancel_"+ dishId).css('display', 'none')
            $("#" + "cancel_"+ dishId).prev().css('display', 'none')
            $("#" + "cancel_"+ dishId).prev().prev().css('display', 'none')
            $("#" + "cancel_"+ dishId).prev().prev().prev().css('display', 'none')
            $("#" + "cancel_"+ dishId).next().css('display', 'none')

        },
        error : function(request,error)
        {
            console.log(error)
        }
    });

    var quantity = parseInt($("#order-detail-table-dishes-quantity").text().split(' ')[0]) - 1
    $("#order-detail-table-dishes-quantity").text(quantity.toString() + ' шт.')

    var quantityForTotal = $(this).parent().children('a')
        .children('.order-detail-table-dish-quantity')
        .children().text().split(' ')[0]
    var quantityForTotalFinal =  parseInt($("#order-detail-table-total-dishes-quantity").text().split(' ')[0]) - parseInt(quantityForTotal)
    $("#order-detail-table-total-dishes-quantity").text(quantityForTotalFinal.toString() + 'шт.')

    var total_by_price_2 = $(this).parent().children('a')
        .children('.order-detail-table-dish-price_2').last()
        .children().text().split(' ')[0]
    var totalByPrice2Final = parseInt($("#order-detail-table-total-by-price-2").text().split(' ')[0]) - parseInt(total_by_price_2)
    $("#order-detail-table-total-by-price-2").text(totalByPrice2Final)

    var total_by_price_1 = parseInt($("#order-detail-table-dish-pirice-1").text()) * parseInt(quantityForTotal)
    var totalByPrice1Final = parseInt($("#order-detail-table-total-by-price-1").text().split(' ')[0]) - parseInt(total_by_price_1)
    $("#order-detail-table-total-by-price-1").text(totalByPrice1Final)

    var diff = totalByPrice2Final - totalByPrice1Final
    $("#order-detail-table-diff").text(diff)

});


function extractDishId(url) {
    var splitedUrl = url.split('/');
    return splitedUrl[splitedUrl.length - 1];
}

function extractSlug(url) {
    var splittedSlug = url.split('/');
    return splittedSlug[splittedSlug.length - 2];
}


$( ".edit-dish-values-submit" ).on( "click", function() {
    var url = $(this).parent().prev().children('a').attr('href')
    var dishId = extractDishId(url)
    var slug = extractSlug(window.location.href)
    var dishQuantity = $(this).prev().prev().children().val()
    var dishPrice2 = $(this).prev().children().val()
    var dishPrice1 = $(this).parent().prev().prev().text()

    if (!dishQuantity) {
        dishQuantity = $(this).parent().prev().children('a')
            .children('.order-detail-table-dish-quantity')
            .children().text()
    }
    if (!dishPrice2) {
        dishPrice2Text = $(this).parent().prev().children('a')
            .children('.order-detail-table-dish-price_2')
            .children().first().text()
        dishPrice2 = dishPrice2Text.split(' ')[0]
    }

    var total = parseInt(dishQuantity) * parseInt(dishPrice2)

    $.ajax({
        url : 'http://localhost:8000/edit_dish/',
        type : 'POST',
        data : {
            'dishId': dishId,
            'slug': slug,
            'dishQuantity': dishQuantity,
            'dishPrice2': dishPrice2
        },
        success : function(data) {
            console.log('Success', data.dishId)
        },
        error : function(request,error)
        {
            console.log(error)
        }
    });

    var totalByPrice2Final = parseInt($("#order-detail-table-total-by-price-2").text().split(' ')[0])
    var quantityForTotal = $(this).parent().prev().children('a')
        .children('.order-detail-table-dish-quantity')
        .children().text().split(' ')[0]
    var finTotalByPrice2 = totalByPrice2Final - parseInt(quantityForTotal) * dishPrice2

    var totalByPrice1Final = parseInt($("#order-detail-table-total-by-price-1").text().split(' ')[0])
    var finTotalByPrice1 = totalByPrice1Final - parseInt(quantityForTotal) * dishPrice1


    var quantityForTotalFinal =  parseInt($("#order-detail-table-total-dishes-quantity").text().split(' ')[0]) - parseInt(quantityForTotal)
    console.log(quantityForTotalFinal, '******')

    $("#order-detail-table-total-dishes-quantity").text((quantityForTotalFinal + parseInt(dishQuantity)).toString() + 'шт.')


    $(this).parent().css('display', 'none')
    $(this).parent().prev().children('a')
        .children('.order-detail-table-dish-quantity')
        .children().text(dishQuantity)
    $(this).parent().prev().children('a')
        .children('.order-detail-table-dish-price_2')
        .children().first().text(dishPrice2)
    $(this).parent().prev().children('a')
        .children('.order-detail-table-dish-price_2')
        .children().last().text(total)

    var quantityForTotalNew = $(this).parent().prev().children('a')
        .children('.order-detail-table-dish-quantity')
        .children().text().split(' ')[0]
    var result = finTotalByPrice2 + parseInt(quantityForTotalNew) * dishPrice2
    var result1 = finTotalByPrice1 + parseInt(quantityForTotalNew) * dishPrice1

    $("#order-detail-table-total-by-price-2").text(result.toString() + ' c.')
    $("#order-detail-table-total-by-price-1").text(result1.toString() + ' c.')
    var diff = result - result1
    $("#order-detail-table-diff").text(diff)

});


$( ".edit-dish" ).on( "click", function() {
    $(this).parent().next().css('display', 'flex')
});