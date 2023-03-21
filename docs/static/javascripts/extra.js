function print_document() {
    document.getElementById("download").style.display = "none"
    window.print();
    document.getElementById("download").style.display = "block"
}
