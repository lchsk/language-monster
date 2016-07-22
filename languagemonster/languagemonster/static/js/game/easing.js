MONSTER.Easing = function()
{

};

MONSTER.Easing.prototype.constructor = MONSTER.Easing;

MONSTER.Easing.linear = function(t){ return t; };
MONSTER.Easing.easeInQuad = function(t){ return t*t; };
MONSTER.Easing.easeOutQuad = function(t){ return t*(2-t); };
MONSTER.Easing.easeInOutQuad = function(t){ return t<0.5 ? 2*t*t : -1+(4-2*t)*t; };
MONSTER.Easing.easeInCubic = function(t){ return t*t*t; };
MONSTER.Easing.easeOutCubic = function(t){ return (--t)*t*t+1; };
MONSTER.Easing.easeInOutCubic = function(t){ return t<0.5 ? 4*t*t*t : (t-1)*(2*t-2)*(2*t-2)+1; };
MONSTER.Easing.easeInQuart = function(t){ return t*t*t*t; };
MONSTER.Easing.easeOutQuart = function(t){ return 1-(--t)*t*t*t; };
MONSTER.Easing.easeInOutQuart = function(t){ return t<0.5 ? 8*t*t*t*t : 1-8*(--t)*t*t*t; };
MONSTER.Easing.easeInQuint = function(t){ return t*t*t*t*t; };
MONSTER.Easing.easeOutQuint = function(t){ return 1+(--t)*t*t*t*t; };
MONSTER.Easing.easeInOutQuint = function(t){ return t<0.5 ? 16*t*t*t*t*t : 1+16*(--t)*t*t*t*t; };
