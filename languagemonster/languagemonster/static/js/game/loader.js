MONSTER.Loader = function(gameObject)
{
  this.game = gameObject;
  this.list = [];
  this.currentID = 0;

  this._prepareMap();
};

MONSTER.Loader.prototype.constructor = MONSTER.Loader;

MONSTER.Loader.prototype._prepareMap = function()
{
  // this.game.map = new MONSTER.MapLoader(this, './test.json');
  // this.list.push(this.game.map);
  this._updateList();
};

MONSTER.Loader.prototype._updateList = function()
{
  this.itemsNumber = this.list.length;
};

MONSTER.Loader.prototype.load = function()
{
  this._loadNext();
};

MONSTER.Loader.prototype.next = function()
{
  this.currentID++;
  this._loadNext();
};

MONSTER.Loader.prototype._loadNext = function()
{
  if (this.currentID < this.itemsNumber)
    this.list[this.currentID].load();
  else
  {
    console.log("Loading finished.");
    
  }
};
