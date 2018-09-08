'use strict';

// Модуль приложения
var main_goods_height = 999999999,
    main_cart_height = 0,
    main_cart_max = false,
    main_goods_table_guids = [],
    main_cart_table_guids = [],
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
        let view_category, guid;
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

            view_category = 'Товары из категории ' + data.node.text;
            guid = data.node.original.href;

            jQuery("#products").replaceWith(main_goods_html);

            widthHeadGoods();
            widthHeadCart();

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

                        jQuery("#goods").html(view_category.link('?sections=' + data.node.original.href));
                        console.log('changed node: ', data);

                        history.pushState(null, null, '/');
                        history.replaceState(null, null, '/');

                        jQuery(window).scrollTop(0);

                        main_goods_table_guids = json.goods_table_guids;
                        main_cart_table_guids = json.cart_table_guids;

                        countHeightTableGoods();
                        countHeightTableCart();

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
                    document.body.querySelectorAll('#goods')
                        .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
                }
            });
        });
    }

    // Загрузка категорий с сервера
    function _loadData() {

        document.body.querySelectorAll('#cart_link_add')
            .forEach( link => link.addEventListener('click', Index._clickQuantityAddCart));
        document.body.querySelectorAll('#cart_link_reduce')
            .forEach( link => link.addEventListener('click', Index._clickQuantityReduceCart))

        widthHeadGoods();
        widthHeadCart();

        $.ajax({
            url: 'ajax/get_categories',
            method: 'GET',
            dataType: 'json',

            success: function(json) {
                // Инициализируем дерево категорий
                if (json.code === 'success') {
                    _initTree(json.result);
                    main_user = json.user_name;
                    main_goods_html = json.goods_html
                    main_cart_table_guids = json.cart_table_guids;
                    countHeightTableCart();
                    updateTables();
                } else {
                    console.error('Ошибка получения данных с сервера: ', json.message);
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

    let window_height = $(window).height(),
        header_height = $('#header').height(),
        header_cart_height = $('#header_cart').height(),
        categories_height = 0,
        goods_table_height = 0,
        cart_table_height = 0;

    cart_table_height = main_cart_height;

    if(document.getElementById("goods_table") && main_goods_table_guids.length !== 0) {
        goods_table_height = (window_height
            - header_cart_height
            - main_cart_height
            - header_height) - 60;

        cart_table_height += Math.max(goods_table_height - main_goods_height, 0)
    }

    if (main_cart_max) {
        cart_table_height -= 20;
    }

    $('#goods_cart').stop().animate({height: cart_table_height});

    goods_table_height = Math.min(goods_table_height, main_goods_height)

    $('#goods_table').stop().animate({height: goods_table_height});

    categories_height = window_height - header_height - 28;

    $('#categories').stop().animate({height: categories_height});
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
    $('th#goods_table_1 div').stop().animate({width: $('#goods_table_1').width() + 3});
    $('th#goods_table_2 div').stop().animate({width: $('#goods_table_2').width() + 3});
    $('th#goods_table_3 div').stop().animate({width: $('#goods_table_3').width() + 3});
    $('th#goods_table_4 div').stop().animate({width: $('#goods_table_4').width() + 3});
    $('th#goods_table_5 div').stop().animate({width: $('#goods_table_5').width() + 3});
    $('th#goods_table_6 div').stop().animate({width: $('#goods_table_6').width() + 3});
    $('th#goods_table_7 div').stop().animate({width: $('#goods_table_7').width() + 3});
}

function countHeightTableGoods() {

    if (main_goods_table_guids.length === 0) {
        window.main_goods_height = 0;
        return;
    }

    let height_ = 20;
    for (let elem in main_goods_table_guids) {
        height_ += $('#tr_good' + main_goods_table_guids[elem]).height();
    }
    window.main_goods_height = height_
}

function countHeightTableCart() {

    if (main_user === '') {
        window.main_cart_max = false;
        window.main_cart_height = 0;
        return;
    }

    let height_ = 20;
    for (let elem in main_cart_table_guids) {
        height_ += $('#tr_cart' + main_cart_table_guids[elem]).height();
    }
    height_ = Math.min(height_, Math.ceil($(window).height() / 3.5));
    window.main_cart_max = height_ >= Math.ceil($(window).height() / 3.5);
    window.main_cart_height = height_
}

jQuery(document).ready(app.init);