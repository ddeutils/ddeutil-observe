// Getting const variable from document.
const sidebar = document.querySelector(".sidebar");
const outsideMain = document.querySelector(".outside-main-wrapper");
const submenuItems = document.querySelectorAll(".submenu_item");
const sidebarOpen = document.querySelector("#sidebarOpen");

// Toggle Sidebar with bottom content
const sidebarExpand = document.querySelector(".expand_sidebar");
const sidebarClose = document.querySelector(".collapse_sidebar");

sidebarOpen.addEventListener("click", () => sidebar.classList.toggle("close"));

sidebarClose.addEventListener("click", () => {
    sidebar.classList.add("close", "hoverable");
    outsideMain.classList.add("close", "hoverable");
});

sidebarExpand.addEventListener("click", () => {
    sidebar.classList.remove("close", "hoverable");
    outsideMain.classList.remove("close", "hoverable");
});

sidebar.addEventListener("mouseenter", () => {
    if (sidebar.classList.contains("hoverable")) {
        sidebar.classList.remove("close");
        outsideMain.classList.remove("close");
    }
});
sidebar.addEventListener("mouseleave", () => {
    if (sidebar.classList.contains("hoverable")) {
        sidebar.classList.add("close");
        outsideMain.classList.add("close");
    }
});

if (window.innerWidth < 768) {
    console.log("InnerWidth less than 768");
    sidebar.classList.add("close");
} else {
    console.log("InnerWidth more than 768");
    sidebar.classList.remove("close");
};

window.addEventListener("resize", function () {
    if (window.innerWidth < 768) {
        console.log("InnerWidth less than 768");
        sidebar.classList.add("close");
        outsideMain.classList.add("close");
    } else {
        console.log("InnerWidth more than 768");
        sidebar.classList.remove("close");
        outsideMain.classList.remove("close");
    };
});



submenuItems.forEach((item, index) => {
    item.addEventListener("click", () => {
        item.classList.toggle("show_submenu");
        submenuItems.forEach((item2, index2) => {
            if (index !== index2) {
                item2.classList.remove("show_submenu");
            }
        });
    });
});
