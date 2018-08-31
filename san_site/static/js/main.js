'use strict';

// Модуль приложения
var app = (function($) {

    // Инициализируем нужные переменные
    var ajaxUrl = 'ajax/get_categories',
        ui = {
            $categories: $('#categories'),
            $goods: $('#goods')
        };

    $(window).resize(function() {
        updateTable();
        widthHeadTable()
    });

    // Инициализация дерева категорий с помощью jstree
    function _initTree(data) {
        var category;
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
            var str_html = 'Товары из категории ' + category;
            ui.$goods.html(str_html.link('?sections=' + data.node.original.href));
            console.log('changed node: ', data);

            var guid = data.node.original.href;

            $('#goods-table-th-1 div').stop().animate({width: 0});
            $('#goods-table-th-2 div').stop().animate({width: 0});
            $('#goods-table-th-3 div').stop().animate({width: 0});
            $('#goods-table-th-4 div').stop().animate({width: 0});
            $('#goods-table-th-5 div').stop().animate({width: 0});

            jQuery("#goods-table").replaceWith("<div id=\"goods-table\"></div>");

            jQuery("#categories ul li a").addClass('disabled');

            jQuery.ajax({
                url: "ajax/get_goods",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success : function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result)
                    {
                        jQuery("#goods-table").replaceWith(json.content); // Заменяем div
                        jQuery(window).scrollTop(0);
                        updateTable();
                        widthHeadTable();
                    }
                    jQuery("#categories ul li a").removeClass('disabled');
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
            data: params,
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
        updateTable();
        fixedId();
    }

    $("html,body").css("overflow","hidden");

    // Экспортируем наружу
    return {
        init: init
    }

})(jQuery);

function updateTable() {
    var clientHeight = ($(window).height() - $('#head').height());
    $('#goods-table').stop().animate({height: clientHeight - 68});
    $('#categories').stop().animate({height: clientHeight - 28});
}

function widthHeadTable() {
    $('#goods-table-th-1 div').stop().animate({width: $('#goods-table-th-1').width() + 5});
    $('#goods-table-th-2 div').stop().animate({width: $('#goods-table-th-2').width() + 5});
    $('#goods-table-th-3 div').stop().animate({width: $('#goods-table-th-3').width() + 5});
    $('#goods-table-th-4 div').stop().animate({width: $('#goods-table-th-4').width() + 5});
    $('#goods-table-th-5 div').stop().animate({width: $('#goods-table-th-5').width() + 3});
}

function fixedId() {
    return;
    var topPadding = 0;
    var offset = $('#categories').offset();
    $(window).scroll(function() {
        if ($(window).scrollTop() > offset.top) {
            var marginTop = $(window).scrollTop() - offset.top + topPadding;
            $('#categories').stop().animate({marginTop: marginTop});
        }
        else {
            $('#categories').stop().animate({marginTop: 0});
        }
    });
}

jQuery(document).ready(app.init);