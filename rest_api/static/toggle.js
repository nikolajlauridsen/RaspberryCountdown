/**
 * Code "stolen" from http://stackoverflow.com/questions/19165866/switch-visibility-between-two-divs
 * and modified ever so slightly by Nikolaj Lauridsen
 */

function toggle_visibility(id1, id2){
    var active = document.getElementById(id1);
    var inactive = document.getElementById(id2);
    if(active.style.display == 'none') {
        active.style.display = 'block';
        inactive.style.display = 'none';
    } else {
        active.style.display = 'none';
        inactive.style.display = 'block';
    }

}