document.getElementById('id-toggle-display').addEventListener('click', function() {
    var ele_sidebar = document.querySelector('.sidebar');
    var ele_sidebar_expand_icon = document.querySelector('.sidebar-expand-icon');
	ele_sidebar.classList.toggle('sidebarpin');
	ele_sidebar_expand_icon.classList.toggle('show');
});