'use strict';

// Модуль приложения
var main_goods_height = 99999,
    main_cart_height = 99999,
    main_list_orders_height = 99999,
    main_goods_items = 0,
    main_cart_max = false,
    main_user = '',
    main_products = '',
    app = (function ($) {

        // Инициализируем нужные переменные
        let ui = {
            categories_resizable: $('#categories_resizable'),
            $categories: $('#categories'),
            goods_table: $('#goods_table'),
            $goods: $('#goods')
        };

        try {
            ui.categories_resizable.css("width", parseFloat(getCookie('categories_width')));
        }catch (e) {}

        countHeightListOrders();

        updateTables();

        widthHeadGoods();
        widthHeadCart();
        widthHeadOrders();

        recoverOnlyStock();
        recoverOnlyPromo();

        $(window).resize(function () {
            updateTables();
            widthHeadGoods();
            widthHeadCart();
            widthHeadOrders();
        });

        $('select[name="payment"]').change( function() {
            if (this.options.selectedIndex+1 === 1) {
                $('.control-group.receiver_bills').css('visibility', 'hidden')
            }else {
                $('.control-group.receiver_bills').css('visibility', 'visible')
            }
        });

        // Инициализация дерева категорий с помощью jstree
        function _initTree(data) {
            let guid;
            ui.$categories.jstree({
                core: {
                    check_callback: true,
                    multiple: false,
                    data: data.result
                },
                types: {
                    default: {
                        valid_children: ["default", "file"]
                    },
                }
            }).bind('changed.jstree', function (e, data) {

                try {
                    guid = data.node.original.href;
                }catch (e) {
                    return
                }

                jQuery("#products").replaceWith(main_products);

                $('#only_promo').prop('checked', false);
                createCookie('is_only_promo', getOnlyPromo(), 30);

                recoverOnlyStock();

                history.pushState(null, null, '/');
                history.replaceState(null, null, '/');

                jQuery("#goods").html('Загрузка товаров...');

                jQuery("#categories ul li a").addClass('disabled');
                jQuery("#loading_icon").removeClass('disabled');

                document.getElementById('goods_table').style.display = 'none';

                jQuery.ajax({
                    url: "ajax/get_goods/",
                    type: 'GET',
                    data: {
                        'guid': guid,
                        'only_stock': getOnlyStock(),
                        'only_promo': getOnlyPromo()
                    },
                    dataType: 'json', // забираем номер страницы, которую нужно отобразить

                    success: function (json) {
                        // Если запрос прошёл успешно и сайт вернул результат
                        if (json.success) {
                            jQuery("#products").replaceWith(json.products);

                            recoverOnlyStock();

                            jQuery("#goods").html('Товары из категории <strong>' + json.current_section
                                .link('?sections=' + guid) + '</strong>');

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
                        jQuery("#loading_icon").addClass('disabled');

                        document.body.querySelectorAll('#goods')
                            .forEach(link => link.addEventListener('click', Index._clickHandlerGoods));

                        onlyStock();
                        onlyPromo();

                    }
                });
            });
            ui.$categories.on('loaded.jstree', function () {
                ui.$categories.jstree(true).deselect_all(true);
                ui.$categories.jstree('select_node', '' + data.guid_initially, true);
            });
        }

        // Инициализация приложения
        function init() {
            $.ajax({
                url: 'ajax/get_categories',
                method: 'GET',
                data: {
                    'only_stock': getOnlyStockFromCookie()
                },
                dataType: 'json',

                success: function (json) {
                    // Инициализируем дерево категорий
                    if (json.success) {
                        _initTree(json);
                        main_user = json.user_name;
                        main_products = json.products;
                        countHeightTableCart();
                        updateTables();
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                },
            });
        }

        onlyStock();
        onlyPromo();

        hiddenOverflow();

        ui.categories_resizable.resizable({
            stop: function( event, ui ) {
                createCookie('categories_width', ui.size.width, 30);
                updateTables();
                widthHeadGoods();
                widthHeadCart();
            }
        });

        // Экспортируем наружу
        return {
            init: init
        }

    })(jQuery);

function updateTables() {

    // language=JQuery-CSS
    let window_height = $(window).height(),
        window_width = $(window).width(),
        header_height = $('#header').height(),
        goods_table_height = 0;

    let available_width = window_width - $('#categories_resizable').width() - 30;

    if (document.getElementById("categories")) {
        $('#categories').stop().animate({height: window_height - header_height - 26});
    }

    if (document.getElementById("list_orders")) {
        let list_orders = $('#list_orders');
        list_orders.stop().animate({
            height: window_height - header_height - $('#list_filter').height() - 38,
            width: available_width
        });
        list_orders.css("width",available_width);
    }

    let cart_table_height = main_cart_height;

    if (document.getElementById("goods_table") && main_goods_items !== 0) {
        goods_table_height = (window_height
            - (document.getElementById("header_cart") ? $('#header_cart').height() : 0)
            - (document.getElementById("goods_search") ? $('#goods_search').height() : 0)
            - (document.getElementById("goods_cart") ? (main_cart_height + (main_cart_max ? 0 : 10)) : -5)
            - header_height) - 65;
        if (document.getElementById("goods_cart")) {
            cart_table_height -= main_cart_max ? 20 : 0;
            cart_table_height += Math.max(goods_table_height - main_goods_height, 0);
        }
    } else {
        if (document.getElementById("form_create_order") === null) {
            cart_table_height = Math.min((window_height
                - (document.getElementById("header_cart") ? $('#header_cart').height() : 0)
                - (document.getElementById("goods_search") ? $('#goods_search').height() : 0)
                - header_height) - 80, main_cart_height);
        } else {
            cart_table_height = Math.min((window_height
                - (document.getElementById("header_cart") ? $('#header_cart').height() : 0)
                - (document.getElementById("form_create_order") ? $('#form_create_order').height() : 0)
                - header_height) - 20, main_cart_height);
        }
    }

    goods_table_height = Math.min(goods_table_height, main_goods_height);

    if (document.getElementById("goods_cart")) {
        let ui_goods_cart = $('#goods_cart');
        ui_goods_cart.stop().animate({
            height: cart_table_height,
            width: available_width
        });
        ui_goods_cart.css("width",available_width);
    }

    if (document.getElementById("goods_table")) {
        let ui_goods_table = $('#goods_table');
        ui_goods_table.stop().animate({
            height: goods_table_height,
            width: available_width
        });
        ui_goods_table.css("width",available_width);
    }

}

function widthHeadCart() {
    let ui_goods_cart = $('#goods_cart');
    ui_goods_cart.css("visibility", "hidden");
    $('th#cart_table_1 div').css("width", $('th#cart_table_1').width());
    $('th#cart_table_2 div').css("width", $('th#cart_table_2').width() + 20);
    $('th#cart_table_3 div').css("width", $('th#cart_table_3').width());
    $('th#cart_table_4 div').css("width", $('th#cart_table_4').width());
    $('th#cart_table_5 div').css("width", $('th#cart_table_5').width());
    $('th#cart_table_6 div').css("width", $('th#cart_table_6').width());
    $('th#cart_table_7 div').css("width", $('th#cart_table_7').width());
    $('th#cart_table_8 div').css("width", $('th#cart_table_8').width());
    ui_goods_cart.css("visibility", "visible");
}

function widthHeadGoods() {
    let ui_goods_cart = $('#goods_cart');
    ui_goods_cart.css("visibility", "hidden");
    $('th#goods_table_1 div').css("width", $('th#goods_table_1').width());
    $('th#goods_table_2 div').css("width", $('th#goods_table_2').width() + 20);
    $('th#goods_table_3 div').css("width", $('th#goods_table_3').width());
    $('th#goods_table_4 div').css("width", $('th#goods_table_4').width());
    $('th#goods_table_5 div').css("width", $('th#goods_table_5').width());
    $('th#goods_table_6 div').css("width", $('th#goods_table_6').width());
    $('th#goods_table_7 div').css("width", $('th#goods_table_7').width());
    $('th#goods_table_8 div').css("width", $('th#goods_table_8').width());
    ui_goods_cart.css("visibility", "visible");
}

function widthHeadOrders() {
    let list_orders = $('#list_orders');
    list_orders.css("visibility", "hidden");
    $('th#orders_table_1 div').css("width", $('th#orders_table_1').width());
    $('th#orders_table_2 div').css("width", $('th#orders_table_2').width());
    $('th#orders_table_3 div').css("width", $('th#orders_table_3').width() + 20);
    $('th#orders_table_4 div').css("width", $('th#orders_table_4').width());
    $('th#orders_table_5 div').css("width", $('th#orders_table_5').width());
    $('th#orders_table_6 div').css("width", $('th#orders_table_6').width());
    $('th#orders_table_7 div').css("width", $('th#orders_table_7').width());
    $('th#orders_table_8 div').css("width", $('th#orders_table_8').width());
    $('th#orders_table_9 div').css("width", $('th#orders_table_9').width());
    list_orders.css("visibility", "visible");
}

function countHeightTableGoods() {

    let height = 20;
    main_goods_items = -1;

    $('#goods_table tr').each(function () {
        height += $(this).height();
        main_goods_items += 1
    });

    if (main_goods_items === 0) {
        height = 0;
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

    if (document.getElementById("goods_table") && main_goods_items !== 0) {
        let limit = document.getElementById("goods_table") ? 3.5 : 2;
        height = Math.min(height, Math.ceil($(window).height() / limit));
        main_cart_max = height >= Math.ceil($(window).height() / limit);
    }

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

function hiddenOverflow() {
  if (document.getElementById("goods_table")
      || document.getElementById("list_orders")) {
          $("html,body").css("overflow", "hidden");
        }
}

function doNav(theUrl) {
    document.location.href = theUrl;
}

function addCart(guid) {
    Index._showFormForQuantity(guid)
}

function showImage(guid) {
    Index._showFormImage(guid)
}

function addQuantityCart(guid) {
    Index._clickQuantityAddCart(guid)
}

function deleteRowCart(guid) {
    Index._clickDeleteRowCart(guid)
}

function reduceQuantityCart(guid) {
    Index._clickQuantityReduceCart(guid)
}

function getOnlyStock() {
    return ($('#only_stock').is(':checked'));
}

function getOnlyStockFromCookie() {
    return getCookie('is_only_stock') === 'true';
}

function getOnlyPromo() {
    return ($('#only_promo').is(':checked'));
}

function getSearchCode() {
    return $('#search_code').val();
}

function searchByCode() {
    Index._changeSelections()
}

function onlyStock() {
    $('#only_stock').click(function () {
        createCookie('is_only_stock', getOnlyStock(), 30);
        Index._changeSelections();
        refreshTree();
    });
}

function onlyPromo() {
    $('#only_promo').click(function () {
        createCookie('is_only_promo', getOnlyPromo(), 30);
        Index._changeSelections();
    });
}

function getCookie(c_name) {
    if (document.cookie.length > 0) {
        let c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            let c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) {
                c_end = document.cookie.length;
            }
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

let createCookie = function (name, value, days) {
    let expires;
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    } else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=/";
};

function recoverOnlyStock() {
    if (getCookie('is_only_stock') === 'true') {
        $('#only_stock').prop('checked', true);
    } else {
        $('#only_stock').prop('checked', false);
    }
}

function recoverOnlyPromo() {
    if (getCookie('is_only_promo') === 'true') {
        $('#only_promo').prop('checked', true);
    } else {
        $('#only_promo').prop('checked', false);
    }
}

function helpQuantity(guid) {
    Index._helpQuantity(guid)
}

function closeBlackOverlay(guid) {
    Index._closeBlackOverlay(guid)
}

function closeBlackOverlayHelp() {
    Index._closeBlackOverlayHelp()
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function refreshTree() {
    $.ajax({
        url: 'ajax/get_categories',
        method: 'GET',
        data: {
            'only_stock': getOnlyStock()
        },
        dataType: 'json',

        success: function (json) {
            if (json.success) {
                let ui = {
                    $categories: $('#categories'),
                };
                ui.$categories.jstree(true).settings.core.data = json.result;
                ui.$categories.jstree(true).refresh(false, true);
                ui.$categories.on("refresh.jstree", function (e) {
                    ui.$categories.jstree(true).deselect_all(true);
                    ui.$categories.jstree('select_node', '' + json.guid_initially, true);
                });
            } else {
                console.error('Ошибка получения данных с сервера');
            }
        },
    });
}

function initiallySelectTree(select_node) {
    $('#categories').jstree("select_node", '' + select_node, true);
}

jQuery(document).ready(app.init);