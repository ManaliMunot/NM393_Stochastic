// You can modify the upload files to pdf's, docs etc
//Currently it will upload only images

/*function readURL(input) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();

                reader.onload = function (e) {
                    $('#blah')
                        .attr('src', e.target.result)
                        .width(150)
                        .height(200);
                };

                reader.readAsDataURL(input.files[0]);
            }
        }*/
$(document).ready(function($) {
    

    // Upload btn on change call function
  $(".uploadlogo").change(function() {  
    var filename = readURL(this);
    $(this).parent().children('span').html(filename);
  });

  // Read File and return value  
  function readURL(input) {
    var url = input.value;
    var ext = url.substring(url.lastIndexOf('.') + 1).toLowerCase();
    if (input.files && input.files[0] && ( ext == "png" || ext == "jpeg" || ext == "jpg" )) {
        
        if (input.files && input.files[0]) {
           var reader = new FileReader();

           reader.onload = function (e) {
                $('.prw_img,#img_1').attr('src', e.target.result).width(120).height(120);
                $('#img_1').css('display','inline');
           };
           reader.readAsDataURL(input.files[0]);
     }
        
     // var path = $(input).val();
     // var filename = path.replace(/^.*\\/, ""); 
       // setTimeout( function () { alert( "Uploaded" )},2000);
      // $('.fileUpload span').html('Uploaded Proof : ' + filename);
      return " Uploaded &#9989";
    } else {
      //$(input).val("");
        alert('only image allowed');
     // return "Only image/pdf formats are allowed!";
    }
  }
  // Upload btn end*/

});

     