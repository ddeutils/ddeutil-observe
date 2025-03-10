htmx.on('htmx:beforeSend', (event) => {
//    event.detail.xhr.abort();
    console.log("Before All HTMX requested");
    console.log(event);
});

htmx.on('htmx:afterRequest', (event) => {
    console.log("After All HTMX requested");
    console.log(event);
});
