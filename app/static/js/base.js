
// toggle-buttonのトリガーとデフォルト値を設定する
// htmlは下記の形で定義し、elmname_div_btn_toggleはdivのid
// <div class="btn_toggle" id="div_xxxx_mode">
//     <input type="checkbox" name="check" />
// </div>
function set_btn_toggle_trigger_and_default(elmname_div_btn_toggle, default_checked){
    let elm_div = $("#"+elmname_div_btn_toggle);

    // トリガーを設定
    elm_div.on("click", function(){
        // div要素のcheckedクラスを反転する
        $(this).toggleClass("checked");

        // div要素以下のinput[name="check"]要素を取得
        let elm_input = $(this).children('input[name="check"]');
        // チェックボックスの値を反転する
        let new_check_stats = !elm_input.prop("checked");
        elm_input.prop("checked", new_check_stats);
        // チェックボックスのチェックイベントを発火
        // （チェックボックスの.change()イベントを使えるように）
        elm_input.prop('checked', new_check_stats).change();
    });

    // デフォルト値を設定
    set_btn_toggle_checked(elmname_div_btn_toggle, default_checked);
}

// toggle-buttonの値を設定する
function set_btn_toggle_checked(elmname_div_btn_toggle, checked){
    let elm_div = $("#"+elmname_div_btn_toggle);
    if (!elm_div) { return; }

    // クラスを設定
    if ( checked ){
        // trueの場合はchecked
        elm_div.addClass("checked");
    } else {
        elm_div.removeClass("checked");
    }
    // チェックボックスの値を設定
    elm_div.children('input[name="check"]').prop("checked", checked);
}
