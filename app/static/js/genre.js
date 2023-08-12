
$(function(){
    $("#tbl_genre td, #tbl_genre th").click(function(){
        // 選択された行のページへ飛ぶ
        let genre_id = $(this).parent().attr("genre_id");
        if( genre_id ){
            window.location.href = main_page_url + "?gn=" + genre_id;
        }
    });
});
