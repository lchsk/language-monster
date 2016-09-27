function setData(obj, key, val)
{
  var ka = key.split(/\./);
  if (ka.length < 2)
  {
    obj[ka[0]] = val;
  }
  else
  {
    if (!obj[ka[0]])
      obj[ka[0]] = {};
    obj = obj[ka.shift()];
    setData(obj, ka.join("."), val);
  }
}

function getData(obj, key)
{
  var ka = key.split(/\./);
  if (ka.length < 2)
  {
      return obj[ka[0]];
  }
  else
  {
    if (!obj[ka[0]])
      obj[ka[0]] = {};
    obj = obj[ka.shift()];
    return getData(obj, ka.join("."));
  }
}

MONSTER.Tween = function(object, variable, targetValue, time)
{
  this.object = object;
  this.variable = variable;
  this.targetValue = targetValue;
  this.time = time;
  this.currentTime = 0;

  this.startValue = getData(this.object, this.variable);

  this.active = true;
};



MONSTER.Tween.prototype.update = function(t)
{
  this.currentTime += t;
  var pct = this.currentTime / this.time;
  var ft = MONSTER.Easing.easeOutCubic(pct);

  var val = Math.round(ft * (this.targetValue - this.startValue)) + this.startValue;

  if (this.active)
  {
    setData(this.object, this.variable, val);
  }

  if (this.currentTime > this.time)
  {
    this.active = false;
  }
};

MONSTER.FuncTimer = function(func, time)
{
  this.func = func;
  this.time = time;
  this.currentTime = 0;

  this.active = true;
};



MONSTER.FuncTimer.prototype.update = function(t)
{
    if (! this.active)
        return;
  this.currentTime += t;

  if (this.active && this.currentTime > this.time)
  {
      this.active = false;
      this.func();
  }
};
