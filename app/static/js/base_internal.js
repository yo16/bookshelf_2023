/* base_internal.js */

$(function(){
    // make_breadcrumbs([]);
});

/* パンくずリストを作る */
function make_breadcrumbs(pages_list){

    let bc_elm = document.getElementById("breadcrumbs");

    let ol = document.createElement("ol");

    for(let i=0; i<pages_list.length; i++){
        let name = pages_list[i][0];
        let url = pages_list[i][1];

        let a = document.createElement("a");
        a.setAttribute("href", url);
        a.textContent = name;

        let li = document.createElement("li");
        li.appendChild(a);
        
        ol.appendChild(li);
    }
    bc_elm.appendChild(ol);
}

