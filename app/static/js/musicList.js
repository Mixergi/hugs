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

jQuery(function($) {
  'use strict'
  var supportsAudio = !!document.createElement('audio').canPlayType;
  if (supportsAudio) {
    // initialize plyr
    var player = new Plyr('#audio1', {
      controls: [
        'play',
        'progress',
        'current-time',
        'duration',
        'mute',
        'volume'
      ]
    });
    // initialize playlist and controls
    var index = 0,
      playing = false,
      mediaPath = 'https://archive.org/download/mythium/',
      extension = '',
      tracks = [{}],
      buildPlaylist = $.each(tracks, function(key, value) {
        var trackNumber = value.track,
          trackName = value.name,
          trackDuration = value.duration;
        if (trackNumber.toString().length === 1) {
          trackNumber = '0' + trackNumber;
        }
        $('#plList').append('<li> \
                <div class="plItem"> \
                    <span class="plNum">' + trackNumber + '</i></span> \
                    <span class="plTitle">' + trackName + '</span> \
                    <span class="plLength" data-placement="top" data-toggle="modal" href="#" data-target="#musicListModal"><i class="fas fa-ellipsis-v"></i></span> \
                </div> \
            </li>');
      }),
      trackCount = tracks.length,
      npAction = $('#npAction'),
      npTitle = $('#npTitle'),
      audio = $('#audio1').on('play', function() {
        playing = true;
        npAction.text('Now Playing...');
      }).on('pause', function() {
        playing = false;
        npAction.text('Paused...');
      }).on('ended', function() {
        npAction.text('Paused...');
        if ((index + 1) < trackCount) {
          index++;
          loadTrack(index);
          audio.play();
        } else {
          audio.pause();
          index = 0;
          loadTrack(index);
        }
      }).get(0),
      btnPrev = $('#btnPrev').on('click', function() {
        if ((index - 1) > -1) {
          index--;
          loadTrack(index);
          if (playing) {
            audio.play();
          }
        } else {
          audio.pause();
          index = 0;
          loadTrack(index);
        }
      }),
      btnNext = $('#btnNext').on('click', function() {
        if ((index + 1) < trackCount) {
          index++;
          loadTrack(index);
          if (playing) {
            audio.play();
          }
        } else {
          audio.pause();
          index = 0;
          loadTrack(index);
        }
      }),
      li = $('#plList li').on('click', function() {
        var id = parseInt($(this).index());
        if (id !== index) {
          playTrack(id);
        }
      }),
      loadTrack = function(id) {
        $('.plSel').removeClass('plSel');
        $('#plList li:eq(' + id + ')').addClass('plSel');
        npTitle.text(tracks[id].name);
        index = id;
        audio.src = mediaPath + tracks[id].file + extension;
        updateDownload(id, audio.src);
      },
      updateDownload = function(id, source) {
        player.on('loadedmetadata', function() {
          $('a[data-plyr="download"]').attr('href', source);
        });
      },
      playTrack = function(id) {
        loadTrack(id);
        audio.play();
      };
    extension = audio.canPlayType('audio/mpeg') ? '.mp3' : audio.canPlayType('audio/ogg') ? '.ogg' : '';
    loadTrack(index);
  } else {
    // no audio support
    $('.column').addClass('hidden');
    var noSupport = $('#audio1').text();
    $('.container').append('<p class="no-support">' + noSupport + '</p>');
  }
});


function myFunction() {
  // Declare variables
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('myInput');
  filter = input.value.toUpperCase();
  ul = document.getElementById("plList");
  li = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("span")[1];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}
