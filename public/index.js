document.getElementById('id-toggle-display').addEventListener('click', function() {
  var ele_sidebar = document.querySelector('.sidebar');
  var ele_sidebar_expand_icon = document.querySelector('.sidebar-expand-icon');
	ele_sidebar.classList.toggle('sidebarpin');
	ele_sidebar_expand_icon.classList.toggle('show');
});

var preview_flag = true;
var stream_var;
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
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    const start = () => mediaRecorder.start();

    const stop = () =>
      new Promise(resolve => {
        mediaRecorder.addEventListener("stop", () => {
          const audioBlob = new Blob(audioChunks);
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          const play = () => audio.play();
          resolve({ audioBlob, audioUrl, play });
        });

        mediaRecorder.stop();
      });

    resolve({ start, stop });
  });

document.getElementById('id-trigger-audio').addEventListener('click', function() {
    const sleep = time => new Promise(resolve => setTimeout(resolve, time));
    (async () => {
	  const recorder = await recordAudio();
	  recorder.start();
	  await sleep(5000);
	  const audio = await recorder.stop();
	  audio.play();
	})();
});

async function recordVideo(start_record_button) {
    // start video preview
    await togglePreview();
    const stop_record_button = document.getElementById("stop_recording");
    start_record_button.setAttribute("disabled","disabled");
    stop_record_button.removeAttribute("disabled");

    new Promise(async resolve => {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true, video: true});
        const mediaRecorder = new MediaRecorder(stream);
        const videoChunks = [];

        mediaRecorder.ondataavailable = e => videoChunks.push(e.data);
        mediaRecorder.onstop = e => downloadVideo(new Blob(videoChunks));

        mediaRecorder.start();
        stop_record_button.addEventListener("click", function () {
            mediaRecorder.stop();
            stop_record_button.setAttribute("disabled","disabled");
            start_record_button.removeAttribute("disabled");
            togglePreview();
            stopStreams(stream);
        });
    });
}
function downloadVideo(blob){
    let a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'recorded.webm';
    document.body.appendChild(a);
    a.click();
}