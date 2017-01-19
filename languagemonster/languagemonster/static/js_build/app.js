window.MONSTER = window.MONSTER || {};

window.MONSTER.is_mobile = function()
{
    return /Mobi/.test(navigator.userAgent);
};

window.MONSTER.is_screen_size_fine = function()
{
    return window.innerWidth > 860;
};

window.MONSTER.has_class = function(ele, cls)
{
    return ele.className.match(new RegExp('(\\s|^)' + cls + '(\\s|$)'));
};

window.MONSTER.remove_class = function(ele, cls)
{
    if (! ele) return;

    if (window.MONSTER.has_class(ele, cls)) {
        var reg = new RegExp('(\\s|^)' + cls + '(\\s|$)');

        ele.className = ele.className.replace(reg, ' ');
    }
};

$(document).ready(function() {
    // Add language box effect

    $('.add-language-box').on("mouseenter", function(){
        var p = $(this).find('.add-language-image');
        p.css("-webkit-filter", "blur(1px)");
        p.css("-moz-filte", "blur(1px)");
        p.css("-o-filter", "blur(1px)");
        p.css("-ms-filter", "blur(1px)");
        p.css("filter", "blur(1px)");

        p.css("transform", "scale(1.2, 1.2)");
        p.css("-ms-transform", "scale(1.2, 1.2)");
        p.css("-webkit-transform", "scale(1.2, 1.2)");

        p.css("transition", "all 0.75s ease-out");
    });

    $('.add-language-box').on("mouseleave", function(){
        var p = $(this).find('.add-language-image');
        p.css("-webkit-filter", "blur(0px)");
        p.css("-moz-filte", "blur(0px)");
        p.css("-o-filter", "blur(0px)");
        p.css("-ms-filter", "blur(0px)");
        p.css("filter", "blur(0px)");

        p.css("transform", "scale(1.0, 1.0)");
        p.css("-ms-transform", "scale(1.0, 1.0)");
        p.css("-webkit-transform", "scale(1.0, 1.0)");

        p.css("transition", "all 0.75s ease-out");
    });

});

$(document).ready(function() {
    $('#btn-unselect-zero').click(function() {
        $('.data_item').each(function() {
            var pop = $(this).find('.pop').html().trim();

            if (pop === 0) {
                var checkbox = $(this).find('.checkbox');
                checkbox.attr('checked', false);
            }
        });
    });

    $('#selectall').click(function() {
        if(this.checked) {
            $('.checkbox').each(function() {
                this.checked = true;
            });
        } else {
            $('.checkbox').each(function() {
                this.checked = false;
            });
        }
    });

    $('.select-group').click(function(e) {
        e.preventDefault();

        var uuid = $(this).attr('data-uuid');

        $('.check-' + uuid).each(function() {
            var checked = $(this).attr('checked');

            $(this).prop('checked', ! $(this).prop('checked'));
        });
    });
});
