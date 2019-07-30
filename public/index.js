// Common Variables
var preview_flag = true;
var stream_var;
var isSessionActive = false;

$('.ui.sidebar').sidebar({
    context: $('.bottom.segment')
  })
  .sidebar('attach events', '.menu .sidebar-trigger')
  .sidebar('setting', 'transition', 'overlay')
  .sidebar('show');

$('.menu .item')
  .tab()
;

$('.ui.accordion')
  .accordion()
;

document.getElementById('id-toggle-display').addEventListener('click', function() {
    var ele_sidebar = document.querySelector('.sidebar');
    var ele_sidebar_expand_icon = document.querySelector('.sidebar-expand-icon');
    ele_sidebar.classList.toggle('sidebarpin');
    ele_sidebar_expand_icon.classList.toggle('show');
});

async function togglePreview() {
    if (preview_flag) {
        if (navigator.mediaDevices.getUserMedia) {
            new Promise(async resolve => {
                const stream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
                stream_var = stream;
                document.getElementById("videoElement").srcObject = stream;
            });
            preview_flag = false;
        }} else {
        stopStreams();
    }
}

function stopStreams(stream){
    if (stream==null){
        stream_var.getTracks().forEach(track => track.stop());
    }
    else{
        stream.getTracks().forEach(track=>track.stop());
    }
    preview_flag=true;
}

const recordAudio = () =>
    new Promise(async resolve => {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });

        const start = () => mediaRecorder.start();

        const stop = (record_start) => {

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks);
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                //audio.play();
                downloadMedia(audioBlob,record_start,'audio');                
            });

            mediaRecorder.stop();
        }
            
        resolve({start, stop});
    });

function updateSessionTimer(element_timer_label){
    let start_time = new Date().getTime();
    // Update the count down every 1 second
    let x = setInterval(function() {

      let now = new Date().getTime();

      let distance = now - start_time;

      // Time calculations for hours, minutes and seconds
      let hours = ("0" + Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).slice(-2);
      let minutes = ("0" + Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))).slice(-2);
      let seconds = ("0" + Math.floor((distance % (1000 * 60)) / 1000)).slice(-2);

      if(isSessionActive){
        document.getElementById("id-label-session-length").innerHTML = hours + ":" + minutes + ":" + seconds;
      }

      if (!isSessionActive) {
        clearInterval(x);
      }
    }, 1000);
}

async function recordVideo(start_record_button) {
    // start video preview
    let record_start=Date();
    isSessionActive = true;
    await togglePreview();
    // start audio capture
    const recorder = await recordAudio();
    recorder.start();
    const stop_record_button = document.getElementById("id-btn-stop-session");
    const pause_record_button = document.getElementById("id-btn-pause-session");
    const session_length_label = document.getElementById("id-label-session-length");

    start_record_button.setAttribute("disabled","disabled");
    stop_record_button.removeAttribute("disabled");
    pause_record_button.removeAttribute("disabled");

    new Promise(async resolve => {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true, video: true});
        const mediaRecorder = new MediaRecorder(stream);
        const videoChunks = [];

        mediaRecorder.ondataavailable = e => videoChunks.push(e.data);
        mediaRecorder.onstop = e => downloadMedia(new Blob(videoChunks),record_start,'video');
        mediaRecorder.start();
        updateSessionTimer(session_length_label);
        stop_record_button.addEventListener("click", function () {            
            mediaRecorder.stop();
            isSessionActive = false;
            // stop and download the audio
            recorder.stop(record_start);            
            stop_record_button.setAttribute("disabled","disabled");
            pause_record_button.setAttribute("disabled","disabled");
            start_record_button.removeAttribute("disabled");
            togglePreview();
            stopStreams(stream);
            session_length_label.innerHTML = "00:00:00";
        });
    });
}

function downloadMedia(blob,record_start,type){
    let record_end=Date();
    let a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    let file_name = "Session_"+ type + "_" + record_start.slice(4,-33)+"_"+record_end.slice(16,-33)+".webm";
    file_name=file_name.split(" ").join("_");
    file_name=file_name.split(":").join(".");
    a.download = file_name;
    document.body.appendChild(a);
    a.click();
}