htmx.on('htmx:afterRequest', (e)=> {
    console.log("After All HTMX requested");
    console.log(e);
});
