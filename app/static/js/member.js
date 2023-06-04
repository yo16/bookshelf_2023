/* member.js */

$(function(){
    //var form_reg_str = 'form[name="frm_regist"]';
    //var form_edit_str = 'form[name="frm_edit"]';
    //var form_del_form_str = 'form[name="frm_delete"]';
    $('input[name="rdo_member_select"]:radio').change(function(){
        //var sel_member_id = $('input[name="rdo_member_select"]').val();
        var member_id = $(this).val();
        var member_name = $(this).attr("member_name");
        var is_admin = ($(this).attr("is_admin")=="True") ? true: false;
        var is_enabled = ($(this).attr("is_enabled")=="True") ? true: false;
        
        $("#edit_member_id").val(member_id);
        $("#edit_member_name").val(member_name);
        $("#editform_is_admin").prop("checked", is_admin);
        var is_admin_val = is_admin ? 1: 0;
        $("#edit_is_admin").val(is_admin_val);
        $("#editform_is_enabled").prop("checked", is_enabled);
        var is_enabled_val = is_enabled ? 1: 0;
        $("#edit_is_enabled").val(is_enabled_val);

        $("#del_member_id").val(member_id);
    })
    
    $("#registform_is_admin").change(function(){
        $("#reg_is_admin").val(
            $(this).prop("checked")? 1: 0
        );
    });
    $("#editform_is_admin").change(function(){
        $("#edit_is_admin").val(
            $(this).prop("checked")? 1: 0
        );
    });
    $("#editform_is_enabled").change(function(){
        $("#edit_is_enabled").val(
            $(this).prop("checked")? 1: 0
        );
    });
});
