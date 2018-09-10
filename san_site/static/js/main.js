'use strict';

// Модуль приложения
var main_goods_height = 99999,
    main_goods_items = 0,
    main_cart_height = 99999,
    main_cart_max = false,
    main_list_orders_height = 99999,
    main_user = '',
    main_goods_html = '',
    app = (function($) {

    // Инициализируем нужные переменные
    let ui = {
            $categories: $('#categories'),
            $goods: $('#goods')
        };

    $(window).resize(function() {
        updateTables();
        widthHeadGoods()
    });

    // Инициализация дерева категорий с помощью jstree
    function _initTree(data) {
        let guid;
        ui.$categories.jstree({
            core: {
                check_callback: true,
                multiple: false,
                data: data
            },
            types: {
                default : {
                    valid_children : ["default","file"]
                },
            }

        }).bind('changed.jstree', function(e, data) {

            guid = data.node.original.href;

            jQuery("#products").replaceWith(main_goods_html);

            widthHeadGoods();
            widthHeadCart();

            jQuery("#goods").html('Грузим товары из категории ' + data.node.text
                .link('?sections=' + data.node.original.href));

            jQuery("#categories ul li a").addClass('disabled');

            jQuery.ajax({
                url: "ajax/get_goods/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success : function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result)
                    {
                        jQuery("#products").replaceWith(json.goods_html);

                        jQuery("#goods").html('Товары из категории ' + data.node.text
                            .link('?sections=' + data.node.original.href));

                        console.log('changed node: ', data);

                        history.pushState(null, null, '/');
                        history.replaceState(null, null, '/');

                        jQuery(window).scrollTop(0);

                        countHeightTableGoods();
                        countHeightTableCart();

                        updateTables();

                        widthHeadGoods();
                        widthHeadCart();
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                    jQuery("#categories ul li a").removeClass('disabled');
                    document.body.querySelectorAll('#goods')
                        .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
                }
            });
        });
    }

    // Загрузка категорий с сервера
    function _loadData() {

        widthHeadGoods();
        widthHeadCart();
        widthHeadOrders();
        countHeightListOrders();

        $.ajax({
            url: 'ajax/get_categories',
            method: 'GET',
            dataType: 'json',

            success: function(json) {
                // Инициализируем дерево категорий
                if (json.code === 'success') {
                    _initTree(json.result);
                    main_user = json.user_name;
                    main_goods_html = json.goods_html;
                    countHeightTableCart();
                    updateTables();
                } else {
                    console.error('Ошибка получения данных с сервера');
                }
            },
        });
    }

    // Инициализация приложения
    function init() {
        _loadData();
    }

    $("html,body").css("overflow","hidden");

    // Экспортируем наружу
    return {
        init: init
    }

})(jQuery);

function updateTables() {

    // language=JQuery-CSS
    let window_height = $(window).height(),
        header_height = $('#header').height(),
        goods_table_height = 0;

    let cart_table_height = main_cart_height;
    let list_orders_table_height = window_height - header_height - 34;

    if (document.getElementById("goods_table") && main_goods_items !== 0) {
        goods_table_height = (window_height
            - $('#header_cart').height()
            - main_cart_height
            - header_height) - 60;
        cart_table_height += Math.max(goods_table_height - main_goods_height, 0);
        cart_table_height -= main_cart_max ? 20 : 0;
    }

    if (document.getElementById("goods_cart")) {
        $('#goods_cart').stop().animate({height: cart_table_height});
    }

    if (document.getElementById("list_orders")) {
        $('#list_orders').stop().animate({height: list_orders_table_height});
    }

    goods_table_height = Math.min(goods_table_height, main_goods_height);

    if (document.getElementById("goods_table")) {
        $('#goods_table').stop().animate({height: goods_table_height});
    }

    let categories_height = window_height - header_height - 28;

    if (document.getElementById("categories")) {
        $('#categories').stop().animate({height: categories_height});
    }
}

function widthHeadCart() {
    $('th#cart_table_1 div').stop().animate({width: $('th#cart_table_1').width()});
    $('th#cart_table_2 div').stop().animate({width: $('th#cart_table_2').width()});
    $('th#cart_table_3 div').stop().animate({width: $('th#cart_table_3').width()});
    $('th#cart_table_4 div').stop().animate({width: $('th#cart_table_4').width()});
    $('th#cart_table_5 div').stop().animate({width: $('th#cart_table_5').width()});
    $('th#cart_table_6 div').stop().animate({width: $('th#cart_table_6').width()});
    $('th#cart_table_7 div').stop().animate({width: $('th#cart_table_7').width()});
}

function widthHeadGoods() {
    $('th#goods_table_1 div').stop().animate({width: $('th#goods_table_1').width()});
    $('th#goods_table_2 div').stop().animate({width: $('th#goods_table_2').width()});
    $('th#goods_table_3 div').stop().animate({width: $('th#goods_table_3').width()});
    $('th#goods_table_4 div').stop().animate({width: $('th#goods_table_4').width()});
    $('th#goods_table_5 div').stop().animate({width: $('th#goods_table_5').width()});
    $('th#goods_table_6 div').stop().animate({width: $('th#goods_table_6').width()});
    $('th#goods_table_7 div').stop().animate({width: $('th#goods_table_7').width()});
}

function widthHeadOrders() {
    $('th#orders_table_1 div').stop().animate({width: $('th#orders_table_1').width()});
    $('th#orders_table_2 div').stop().animate({width: $('th#orders_table_2').width()});
    $('th#orders_table_3 div').stop().animate({width: $('th#orders_table_3').width()});
    $('th#orders_table_4 div').stop().animate({width: $('th#orders_table_4').width()});
    $('th#orders_table_5 div').stop().animate({width: $('th#orders_table_5').width()});
    $('th#orders_table_6 div').stop().animate({width: $('th#orders_table_6').width()});
    $('th#orders_table_7 div').stop().animate({width: $('th#orders_table_7').width()});
}

function countHeightTableGoods() {

    let height = 20;
    main_goods_items = -1;

    $('#goods_table tr').each(function () {
        height += $(this).height();
        main_goods_items += 1
    });

    if (main_goods_items === 0) {
        window.main_goods_height = 0;
        return;
    }

    main_goods_height = height
}

function countHeightTableCart() {

    if (main_user === '') {
        main_cart_max = false;
        main_cart_height = 0;
        return;
    }

    let height = 20;

    $('#goods_cart tr').each(function () {
        height += $(this).height();
    });

    let limit = document.getElementById("goods_table") ? 3.5 : 2;
    height = Math.min(height, Math.ceil($(window).height() / limit));

    main_cart_max = height >= Math.ceil($(window).height() / limit);
    main_cart_height = height
}

function countHeightListOrders() {

    let height = 20;

    $('#list_orders tr').each(function () {
        height += $(this).height();
    });

    let limit = 2;
    height = Math.min(height, Math.ceil($(window).height() / limit));

    main_list_orders_height = height
}

function doNav(theUrl) {
    document.location.href = theUrl;
}

function addCart(guid) {
    Index._clickAddCart(guid)
}

function addQuantityCart(guid) {
    Index._clickQuantityAddCart(guid)
}

function reduceQuantityCart(guid) {
    Index._clickQuantityReduceCart(guid)
}

jQuery(document).ready(app.init);