
$(function(){
    $("#tbl_genre td, #tbl_genre th").click(function(){
        let genre_id = $(this).attr("genre_id");
        let rdo_genre = $("#rdo_genre_"+genre_id);
        rdo_genre.prop("checked", true);
    });

    $("#btn_sort_up").click(function(){
        
    });
});
