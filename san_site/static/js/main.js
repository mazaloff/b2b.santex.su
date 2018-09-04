'use strict';

// Модуль приложения
var main_goods_height = 0,
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

                        updateTables(Number(json.cart_height), Number(json.goods_height));
                        widthHeadGoods();
                        widthHeadCart();
                    }
                    jQuery("#categories ul li a").removeClass('disabled');
                    document.body.querySelectorAll('#cart_add')
                        .forEach( link => link.addEventListener('click', Index._clickAddCart) );
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

function updateTables(cart_height=undefined, goods_height=undefined) {

    var window_height = $(window).height(),
        header_height = $('#header').height(),
        header_cart_height = $('#header_cart').height(),
        categories_height = window_height - header_height - 28,
        goods_table_height = 0;

    cart_height = (cart_height === undefined) ? $('#goods_cart').height() : cart_height;
    cart_height = (cart_height === 0) ? 0 : cart_height;

    goods_height = (goods_height === undefined) ? window.main_goods_height : goods_height;
    goods_height = (goods_height === undefined) ? 999999999 : goods_height;

    goods_table_height = (window_height -
                            header_cart_height -
                            ((cart_height === 0) ? 0 : cart_height + 24)
                            - header_height) - 60;
    window.main_goods_height = goods_height;

    $('#goods_table').stop().animate({height: Math.min(goods_table_height, goods_height)});
    $('#categories').stop().animate({height: categories_height});

    if (cart_height !== undefined && cart_height !== 0) {
        $('#goods_cart').stop().animate({height: (cart_height +
            Math.max(0, goods_table_height - goods_height - 60))});
    }

}

function widthHeadCart() {
    $('th#cart_table_1 div').stop().animate({width: $('#cart_table_1').width() + 5});
    $('th#cart_table_2 div').stop().animate({width: $('#cart_table_2').width() + 5});
    $('th#cart_table_3 div').stop().animate({width: $('#cart_table_3').width() + 5});
    $('th#cart_table_4 div').stop().animate({width: $('#cart_table_4').width() + 5});
    $('th#cart_table_5 div').stop().animate({width: $('#cart_table_5').width() + 5});
}

function widthHeadGoods() {
    $('th#goods_table_1 div').stop().animate({width: $('#goods_table_1').width() + 5});
    $('th#goods_table_2 div').stop().animate({width: $('#goods_table_2').width() + 5});
    $('th#goods_table_3 div').stop().animate({width: $('#goods_table_3').width() + 5});
    $('th#goods_table_4 div').stop().animate({width: $('#goods_table_4').width() + 5});
    $('th#goods_table_5 div').stop().animate({width: $('#goods_table_5').width() + 5});
    $('th#goods_table_6 div').stop().animate({width: $('#goods_table_6').width() + 5});
}

jQuery(document).ready(app.init);