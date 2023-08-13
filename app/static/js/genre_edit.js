
$(function(){
    $("#tbl_genre td, #tbl_genre th").click(function(){
        // tr要素にgenre_idを設定しているので取得して、ラジオボタンを選択
        let genre_id = $(this).parent().attr("genre_id");
        let rdo_genre = $("#rdo_genre_"+genre_id);
        rdo_genre.prop("checked", true);

        // ラジオボタン変更処理
        changed_genre(rdo_genre);
    });

    $("#btn_genre_sort_up").click(function(){
        $("#edit_order_delta").val(-1);
        $("#frm_edit_order").submit();
    });

    $("#btn_genre_sort_down").click(function(){
        $("#edit_order_delta").val(1);
        $("#frm_edit_order").submit();
    });

    // ラジオボタンでジャンルを選択したとき
    $("input[name='rdo_genre_select']").change(function(){
        changed_genre($(this));
    });

    // 初期値設定
    initialize_settings();
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

    // 並び順編集用
    $("#edit_order_genre_id").val(genre_id);

    // 削除用
    // 削除の場合は、選択したジャンルが削除対象
    $("#txt_delete_genre_id").val(genre_name);
    $("#del_genre_id").val(genre_id);
}

// 初期値設定
function initialize_settings(){
    // ジャンルの選択
    function set_genre_rdo(){
        // 順序編集用の値が設定されていたら、対応するラジオボタンをチェックする
        let rdo_genre = $("#rdo_genre_"+default_select_genre_id);
        rdo_genre.prop("checked", true);

        console.log(default_select_genre_id);

        // ラジオボタン変更処理
        changed_genre(rdo_genre);
    }

    // デフォルトのメニュー
    function set_menu(){
        if (default_select_menu=="regist"){
            $("#rdo_add_genre").prop("checked", true);
        } else if (default_select_menu=="edit"){
            $("#rdo_edit_genre").prop("checked", true);
        } else if (default_select_menu=="delete"){
            $("#rdo_delete_genre").prop("checked", true);
        }
    }

    if( default_select_genre_id != "None" ){ set_genre_rdo(); }
    $("#rdo_add_genre").prop("checked", true);
    if( default_select_menu != "None" ){ set_menu(); }
}

