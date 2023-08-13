/* main.js */

$(function(){
    $("#div_display_style input[name='rdo_display_style']").click(function(){
        let next_style = $("#div_display_style input[name='rdo_display_style']:checked").val();
        set_display_style(next_style);
    });
});

function set_display_style(str_style){
    let div = $("#div_books_display_style");
    div.removeClass();

    if (str_style=="grid_small"){
        div.addClass("books_grid_small");
    } else if (str_style=="grid_large"){
        div.addClass("books_grid_large");
    } else if (str_style=="list"){
        div.addClass("books_list");
    }
}
