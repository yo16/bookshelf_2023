
$(function(){
    $("#tbl_genre td, #tbl_genre th").click(function(){
        let genre_id = $(this).attr("genre_id");
        let rdo_genre = $("#rdo_genre_"+genre_id);
        rdo_genre.prop("checked", true);

        // ラジオボタン変更処理
        changed_genre(rdo_genre);
    });

    $("#btn_sort_up").click(function(){

    });

    // ジャンル一覧テーブルで選択したとき
    $("input[name='rdo_genre_select']").change(function(){
        changed_genre($(this));
    });
});

// ジャンル変更時に、フォームに設定する
function changed_genre(rdo_genre){
    let parent_genre_id = rdo_genre.attr("parent_genre_id");
    let genre_id = rdo_genre.attr("genre_id");
    let genre_name = rdo_genre.attr("genre_name");

    // 新規用
    // 新規の場合は、選択したジャンルが親
    $("#reg_parent_genre_id").val(genre_id);
    $("#txt_regist_parent_genre").val(genre_name);

    // 編集用
    // 編集の場合は、選択したジャンルが編集対象
    $("#sel_edit_parent_genre_id").val(parent_genre_id);
    $("#edit_parent_genre_id").val(parent_genre_id);
    $("#edit_genre_id").val(genre_id);
    $("#edit_genre_name").val(genre_name);

    // 削除用
    // 削除の場合は、選択したジャンルが削除対象
    $("#txt_delete_genre_id").val(genre_name);
    $("#del_genre_id").val(genre_id);
}
