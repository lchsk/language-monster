function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function setupAjax()
{
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
          // Only send the token to relative URLs i.e. locally.
          xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
      }
    });
}

$(document).ready(function() {
    // Used in admin pages
    $('#btn-unselect-zero').click(function(event) {
        $('.data_item').each(function() {
            var pop = $(this).find('.pop').html().trim();

            if (pop === 0) {
                var checkbox = $(this).find('.checkbox');
                checkbox.attr('checked', false);
            }
        });
    });

    // Used in admin pages
    $('#selectall').click(function(event) {
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

    // admin pages
    var get_words = function()
    {
        var items = $('tr.data_item');
        var d = {};

        for (var i = 0; i < items.length; i++)
        {
            var tmp = {};
            var id = items[i].id;
            var save = $('#' + id).find('input.save').first();
            var base = $('#' + id).find('input.base').first();
            var target = $('#' + id).find('input.target').first();

            if (save.length == 1)
                tmp.save = save[0].checked;

            if (base.length == 1)
                tmp.base = base[0].value;

            if (target.length == 1)
                tmp.target = target[0].value;

            d[id] = tmp;
        }

        return d;
    };

    // var save_edit_words_form = function(words, save_link, redirect_link)
    // {
    //     $.ajax({
    //         method: "POST",
    //         url: save_link,
    //         //   crossDomain: false,
    //         //   contentType: "application/json",
    //         //   dataType: "json",
    //         data: {
    //             'json': JSON.stringify(words)
    //         }
    //     })
    //     .success(function(msg){
    //         alert( "Sent successfully");
    //         window.location = redirect_link;
    //     });
    // }

    // var get_links = function()
    // {
    //     return {
    //         'save_link': $('#save_link').val(),
    //         'redirect_link': $('#redirect_link').val()
    //     }
    // }

    // $('#submit_edited_words').on('click', function()
    // {
    //     var words = get_words();
    //     var links = get_links();
    //     setupAjax();
    // 
    //     save_edit_words_form(words, links.save_link, links.redirect_link)
    // 
    //     // return false;
    // });

    // $('#submit_edited_words').on('click', function()
    // {
    //     var words = get_words();
    //     var links = get_links();
    //     setupAjax();
    // 
    //     save_edit_words_form(words, links.save_link, links.redirect_link)
    // 
    //     // return false;
    // });

    // ----

    $('#modal-report-error').on('shown.bs.modal', function(){
        $('#form-report-error-text').focus();
    });

    $('#form-report-error-submit').on('click', function(e){
        e.preventDefault();

        var username  = $('#form-report-error-username').val();
        var dataset_id = $('#form-report-error-dataset_id').val();
        var text = $('#form-report-error-text').val();

        if (text.length <= 0)
        {
            $('#modal-report-error .alert').hide();
            $('#form-report-alert-too_short').fadeIn();

            return false;
        }

        var d = {};
        d.username = username;
        d.dataset_id = dataset_id;
        d.text = text;

        setupAjax();

        $.ajax({
          method: "POST",
          url: '/languages/error',
          data: { 'json': JSON.stringify(d) }
        })
          .success(function( msg )
          {
              $('#modal-report-error .alert').hide();
              $('#form-report-error-div').hide();
              $('#form-report-alert-success').fadeIn();

          })
          .error(function(msg){
              $('#modal-report-error .alert').hide();
              $('#form-report-alert-failure').fadeIn();
          });

        return false;
    });


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
