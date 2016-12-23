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
