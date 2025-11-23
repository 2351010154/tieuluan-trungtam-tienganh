 const hamburger = document.querySelector('#toggle-btn');

 hamburger.addEventListener("click",function() {
    document.querySelector("#sidebar").classList.toggle("expand");
 })


let debounceTimeOut = null;
function debounceSearch() {
    var searchForm = document.getElementById('search-form');

    if (debounceTimeOut != null) {
        clearTimeout(debounceTimeOut);
    }
    debounceTimeOut = setTimeout(() => {
        searchForm.submit();
    },500);
}