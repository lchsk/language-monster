$('.modal-fix').bind('hidden.bs.modal', function () {
  $("html").css("margin-right", "0px");
});
$('.modal-fix').bind('show.bs.modal', function () {
  $("html").css("margin-right", "-15px");
});
