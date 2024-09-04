function print_document() {
    document.getElementById("download").style.display = "none"
    window.print();
    document.getElementById("download").style.display = "block"
}

function show_modal(id) {
    var modal = document.getElementById("modal");
    modal.style.display = "block";
    var contents = document.getElementById(id).innerHTML;
    document.getElementById("modal-body").innerHTML = contents;

    // When the user clicks on (x), close the modal
    var span = document.getElementsByClassName("close")[0];
    span.onclick = function() {
      modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }
}