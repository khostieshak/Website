var windowWidth=$(window).outerWidth();
var windowHeight=$(window).height();
//$("#header-img").height(windowHeight-30);

$(window).resize(function() {
    windowWidth=$(window).outerWidth();
    windowHeight=$(window).height()
    //$("#header-img").height(windowHeight-30);
});

$(function () {
    $(window).scroll(function () {
        if(windowWidth>768) {
            var x = $(window).scrollTop();
            if (x >= windowHeight) {
                $("#navbar-logo").removeClass('d-md-none');
            } else {
                $("#navbar-logo").addClass('d-md-none');
            }
        }
    });
});

$('.content').on('click', '.article-link', function (event) {
    event.preventDefault();
    var info=$(this).data("info");
    $.ajax({
        url: $(this).data("src"),
        success: function (data) {
            $("#article-list").html(data);
            $("#search-info").html(info);
        }
    });
});
