//datatable
$(document).ready(function() {
  $('#tabela1').DataTable({
    "searching": false // false to disable search (or any other option)
  });
  $('.dataTables_length').addClass('bs-select');
});

//search form table toggle
$('.table-responsive').on('click', '.search-toggle', function(e) {
  var selector = $(this).data('selector');

  $(selector).toggleClass('show').find('.search-input').focus();
  $(this).toggleClass('active');

  e.preventDefault();
});

//filter input for table
$("#myInput").on("keyup", function() {
  var value = $(this).val().toLowerCase();
  $("#tabela1 tr").filter(function() {
    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
  });
});

function url_copy() {
  var copyText = document.getElementById("musicURL");
  copyText.select();
  document.execCommand("Copy");
}
