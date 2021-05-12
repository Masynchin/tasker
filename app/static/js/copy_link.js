function copyLink(link) {
    navigator.clipboard.writeText(link)
        .catch(err => {
            console.log(err);
        });
}
