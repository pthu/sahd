function print_document() {
const doc = new jsPDF();

    window.print();
}

function print_document2() {
    document.getElementById("download").style.display = "none"
    window.print();
    document.getElementById("download").style.display = "block"
}
