var preview_flag = true;
var stream_var;
function showPreview() {
    const preview_div = document.getElementById("preview_div");
    if(preview_flag){
        // if(preview_div.style.display==="none"||preview_div.style.display==="") {
            // var preview_div=document.getElementById("preview_div");
            if (navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({video: true})
                    .then(function (stream) {
                        stream_var=stream;
                        document.getElementById("videoElement").srcObject = stream;
                    })
                    .catch(function (error) {
                        console.log("Something went wrong!", error);
                    });
            }
            preview_flag=false;
        // }
    }
    else{
        hideDiv();
    }
}

function hideDiv(){
    var track = stream_var.getTracks()[0];
    track.stop();
    // const preview_div = document.getElementById("preview_div");
    // preview_div.style.display="none";
    preview_flag=true;

}