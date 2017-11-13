header();
function header() {
    var windowWidth=$(window).outerWidth();
    var windowHeight=$(window).height();
    if(windowWidth<768) {
        $("#navbar-logo").removeClass('invisible');
    }
    if(windowWidth>768) {
        var x = $(window).scrollTop();
        if (x >= 0.3 * windowHeight ) {
            $("#navbar-logo").removeClass('invisible');
            $(".header-img").css('height', 0 );
        } else {
            $(".header-img").css('height', 0.3 * windowHeight - x);

            $("#navbar-logo").addClass('invisible');

        }
        $("#footer-img").css('height', $("#footer-text").height());
    }
}


$(window).resize(function() {
    header();
});

$(window).scroll(function () {
        header();
});



$('.main-content').on('click', '.article-link', function (event) {
    event.preventDefault();
    if ($("#article-list").length>0) {
        var info = $(this).data("info");
        $.ajax({
            url: $(this).data("src"),
            success: function (data) {
                $("#article-list").html(data);
                $("#search-info").html(info);
                $(window).scrollTop($('#article-list').offset().top - 100);
            }
        });
    }else{
        window.location.replace("/");
    }
});


$('[data-toggle="tooltip"]').tooltip();