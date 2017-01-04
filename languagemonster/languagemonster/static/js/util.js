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
