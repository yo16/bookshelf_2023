/* member.js */

$(function(){
    // tdをクリック時
    $("#tbl_members td").click(function(){
        // tr要素にmember_idが設定されているので取得
        let member_id = $(this).parent().attr("member_id");
        if( member_id ){
            let rdo_member = $("#rdo_member_select_" + member_id);
            rdo_member.prop("checked", true);

            // ラジオボタン変更処理
            changed_member(rdo_member);
        }
    });
    // ラジオボタン変更時
    $('input[name="rdo_member_select"]:radio').change(function(){
        // ラジオボタン変更処理
        changed_member($(this));
    });
    
    // タブ切り替え時
    // 追加
    $("#registform_is_admin").change(function(){
        $("#reg_is_admin").val(
            $(this).prop("checked")? 1: 0
        );
    });
    // 編集
    $("#editform_is_admin").change(function(){
        $("#edit_is_admin").val(
            $(this).prop("checked")? 1: 0
        );
    });
    // 削除
    $("#editform_is_enabled").change(function(){
        $("#edit_is_enabled").val(
            $(this).prop("checked")? 1: 0
        );
    });
});


function changed_member(rdo_member){
    //var sel_member_id = $('input[name="rdo_member_select"]').val();
    var member_id = rdo_member.val();
    var member_name = rdo_member.attr("member_name");
    var member_code = rdo_member.attr("member_code");
    var is_admin = (rdo_member.attr("is_admin")=="True") ? true: false;
    var is_enabled = (rdo_member.attr("is_enabled")=="True") ? true: false;
    
    $("#edit_member_id").val(member_id);
    $("#edit_member_name").val(member_name);
    $("#edit_member_code").val(member_code);
    $("#editform_is_admin").prop("checked", is_admin);
    var is_admin_val = is_admin ? 1: 0;
    $("#edit_is_admin").val(is_admin_val);
    $("#editform_is_enabled").prop("checked", is_enabled);
    var is_enabled_val = is_enabled ? 1: 0;
    $("#edit_is_enabled").val(is_enabled_val);

    $("#del_member_id").val(member_id);
    $("#del_member_name").val(member_name);
    $("#del_member_code").val(member_code);
    $("#del_is_admin").prop("checked", is_admin);
    $("#del_is_enabled").prop("checked", is_enabled);
};
