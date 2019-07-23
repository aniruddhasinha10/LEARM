document.getElementById('id-toggle-display').addEventListener('click', function () {
    const ele_sidebar = document.querySelector('.sidebar');
    const ele_sidebar_expand_icon = document.querySelector('.sidebar-expand-icon');
    ele_sidebar.classList.toggle('sidebarpin');
    ele_sidebar_expand_icon.classList.toggle('show');
});

let preview_flag = true;
let stream_var;

function showPreview() {
    // const preview_div = document.getElementById("preview_div");
    if (preview_flag) {
        // if(preview_div.style.display==="none"||preview_div.style.display==="") {
        // var preview_div=document.getElementById("preview_div");
        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({video: true})
                .then(function (stream) {
                    stream_var = stream;
                    document.getElementById("videoElement").srcObject = stream;
                })
                .catch(function (error) {
                    console.log("Something went wrong!", error);
                });
        }
        preview_flag = false;
        // }
    } else {
        hideDiv();
    }
}

function hideDiv() {
    const track = stream_var.getTracks()[0];
    track.stop();
    // const preview_div = document.getElementById("preview_div");
    // preview_div.style.display="none";
    preview_flag = true;

}

const recordAudio = () =>
    new Promise(async resolve => {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        // noinspection JSUnresolvedFunction
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
                    resolve({audioBlob, audioUrl, play});
                });

                mediaRecorder.stop();
            });

        resolve({start, stop});
    });

document.getElementById('id-trigger-audio').addEventListener('click', function () {
    const sleep = time => new Promise(resolve => setTimeout(resolve, time));
    (async () => {
        const recorder = await recordAudio();
        recorder.start();
        await sleep(5000);
        const audio = await recorder.stop();
        audio.play();
    })();
});
