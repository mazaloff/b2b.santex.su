'use strict';

// Модуль приложения
var main_goods_height = 999999999,
    main_cart_height = 0,
    main_cart_max = false,
    app = (function($) {

    // Инициализируем нужные переменные
    var ajaxUrl = 'ajax/get_categories',
        ui = {
            $categories: $('#categories'),
            $goods: $('#goods')
        };

    $(window).resize(function() {
        updateTables();
        widthHeadGoods()
    });

    // Инициализация дерева категорий с помощью jstree
    function _initTree(data) {
        var category, str_category, guid;
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

            category = data.node.text;
            str_category = 'Товары из категории ' + category;
            guid = data.node.original.href;

            ui.$goods.html(str_category.link('?sections=' + data.node.original.href));
            console.log('changed node: ', data);

            $('th#goods_table_1 div').stop().animate({width: 0});
            $('th#goods_table_2 div').stop().animate({width: 0});
            $('th#goods_table_3 div').stop().animate({width: 0});
            $('th#goods_table_4 div').stop().animate({width: 0});
            $('th#goods_table_5 div').stop().animate({width: 0});
            $('th#goods_table_6 div').stop().animate({width: 0});

            $('th#cart_table_1 div').stop().animate({width: 0});
            $('th#cart_table_2 div').stop().animate({width: 0});
            $('th#cart_table_3 div').stop().animate({width: 0});
            $('th#cart_table_4 div').stop().animate({width: 0});
            $('th#cart_table_5 div').stop().animate({width: 0});
            $('th#cart_table_6 div').stop().animate({width: 0});
            $('th#cart_table_7 div').stop().animate({width: 0});

            jQuery("#goods_table").replaceWith("<div id=\"goods_table\"></div>");
            jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");
            jQuery("#goods_cart").replaceWith("<div id=\"goods_cart\"></div>");

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
                        jQuery("#goods_table").replaceWith(json.goods_table);
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#goods_cart").replaceWith(json.goods_cart);

                        jQuery(window).scrollTop(0);

                        countHeightTableGoods(json.goods_table_guids);
                        countHeightTableCart(json.cart_table_guids);

                        updateTables();
                        widthHeadGoods();
                        widthHeadCart();
                    }
                    jQuery("#categories ul li a").removeClass('disabled');
                    document.body.querySelectorAll('#cart_add')
                        .forEach( link => link.addEventListener('click', Index._clickAddCart));
                    document.body.querySelectorAll('#cart_link_add')
                        .forEach( link => link.addEventListener('click', Index._clickQuantityAddCart));
                    document.body.querySelectorAll('#cart_link_reduce')
                        .forEach( link => link.addEventListener('click', Index._clickQuantityReduceCart));
                }
            });
        });
    }

    // Загрузка категорий с сервера
    function _loadData() {
        var params = {
            action: 'get_categories'
        };

        $.ajax({
            url: ajaxUrl,
            method: 'GET',
            dataType: 'json',
            success: function(resp) {
                // Инициализируем дерево категорий
                if (resp.code === 'success') {
                    _initTree(resp.result);
                } else {
                    console.error('Ошибка получения данных с сервера: ', resp.message);
                }
            },
            error: function(error) {
                console.error('Ошибка: ', error);
            }
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

    var window_height = $(window).height(),
        header_height = $('#header').height(),
        header_cart_height = $('#header_cart').height(),
        categories_height = 0,
        goods_table_height = 0,
        cart_table_height = 0;

    goods_table_height = (window_height
                            - header_cart_height
                            - window.main_cart_height
                            - header_height) - 60;

    cart_table_height = window.main_cart_height +
            Math.max(goods_table_height - window.main_goods_height, 0)
    if (window.main_cart_max) {
        cart_table_height -= 20;
    }

    if (cart_table_height > 0) {
        $('#goods_cart').stop().animate({height: cart_table_height});
    }

    goods_table_height = Math.min(goods_table_height, window.main_goods_height)

    if (goods_table_height > 0) {
        $('#goods_table').stop().animate({height: goods_table_height});
    }

    categories_height = window_height - header_height - 28;

    if (categories_height > 0) {
        $('#categories').stop().animate({height: categories_height});
    }
}

function widthHeadCart() {
    $('th#cart_table_1 div').stop().animate({width: $('#cart_table_1').width() + 5});
    $('th#cart_table_2 div').stop().animate({width: $('#cart_table_2').width() + 5});
    $('th#cart_table_3 div').stop().animate({width: $('#cart_table_3').width() + 5});
    $('th#cart_table_4 div').stop().animate({width: $('#cart_table_4').width() + 5});
    $('th#cart_table_5 div').stop().animate({width: $('#cart_table_5').width() + 5});
    $('th#cart_table_6 div').stop().animate({width: $('#cart_table_6').width() + 5});
    $('th#cart_table_7 div').stop().animate({width: $('#cart_table_7').width() + 5});
}

function widthHeadGoods() {
    $('th#goods_table_1 div').stop().animate({width: $('#goods_table_1').width() + 5});
    $('th#goods_table_2 div').stop().animate({width: $('#goods_table_2').width() + 5});
    $('th#goods_table_3 div').stop().animate({width: $('#goods_table_3').width() + 5});
    $('th#goods_table_4 div').stop().animate({width: $('#goods_table_4').width() + 5});
    $('th#goods_table_5 div').stop().animate({width: $('#goods_table_5').width() + 5});
    $('th#goods_table_6 div').stop().animate({width: $('#goods_table_6').width() + 5});
}

function countHeightTableGoods(array) {

    var height_ = 20;
    for (var elem in array) {
        height_ += $('#tr_good' + array[elem]).height();
    }
    window.main_goods_height = height_
}

function countHeightTableCart(array) {

    var height_ = 20;
    for (var elem in array) {
        height_ += $('#tr_cart' + array[elem]).height();
    }
    height_ = Math.min(height_, Math.ceil($(window).height() / 3.5));
    window.main_cart_max = height_ >= Math.ceil($(window).height() / 3.5);
    window.main_cart_height = height_
}

jQuery(document).ready(app.init);