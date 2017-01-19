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
