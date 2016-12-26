window.MONSTER = window.MONSTER || {};

window.MONSTER.is_mobile = function()
{
    return /Mobi/.test(navigator.userAgent);
};

window.MONSTER.is_screen_size_fine = function()
{
    return window.innerWidth > 860;
};
