function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle-btn');

    sidebar.classList.toggle('collapsed');
    toggleButton.classList.toggle('rotate');

    closeAllSubMenus();

    document.getElementById('main-content').classList.toggle('expanded');
}

function toggleSubMenu(button){

    if(!button.nextElementSibling.classList.contains('show')){
        closeAllSubMenus()
    }

    button.nextElementSibling.classList.toggle('show')
    button.classList.toggle('rotate')

    if(sidebar.classList.contains('close')){
        sidebar.classList.toggle('close')
        toggleButton.classList.toggle('rotate')
    }
}

function closeAllSubMenus(){
    Array.from(sidebar.getElementsByClassName('show')).forEach(ul => {
        ul.classList.remove('show')
        ul.previousElementSibling.classList.remove('rotate')
    })
}
