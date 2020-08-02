$(document).ready(function() {

    $('.updateButton').on('click', function() {

        var member_id = $(this).attr('member_id');

        req = $.ajax({
            url : '/verify',
            type : 'POST',
            data : { id : member_id }
        });
            // $('#fading'+member_id).fadeOut(1000)
            $('#fading'+member_id).toggle('slow');


    });

    $('.updateButtoncross').on('click', function() {

        var member_id = $(this).attr('member_id');


        req = $.ajax({
            url : '/verify_not',
            type : 'POST',
            data : { id : member_id }
        });
        $('#fading'+member_id).toggle('slow');



    });



});
