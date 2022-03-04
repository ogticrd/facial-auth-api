let cedula = prompt('Introduce your cedula: ')

let preview = document.getElementById("preview");
let recording = document.getElementById("recording");
let startButton = document.getElementById("startButton");
let stopButton = document.getElementById("stopButton");
let downloadButton = document.getElementById("downloadButton");
let logElement = document.getElementById("log");

let recordingTimeMS = 2000;
let challenge = null
let recursion_count = 0
const options = {
  video: true,
  mimeType : 'video/webm'
}

const socket = io()

socket.on('result', result => {
  console.log(result)
})

function log(msg) {
  logElement.innerHTML += msg + "\n";
}

function wait(delayInMS) {
  return new Promise(resolve => setTimeout(resolve, delayInMS));
}

function startRecording(stream, lengthInMS) {
  let recorder = new MediaRecorder(stream);
  let data = [];

  recorder.ondataavailable = event => data.push(event.data);
  recorder.start();
  log(recorder.state + " for " + (lengthInMS/1000) + " seconds...");

  let stopped = new Promise((resolve, reject) => {
    recorder.onstop = resolve;
    recorder.onerror = event => reject(event.name);
  });

  let recorded = wait(lengthInMS).then(
    () => recorder.state == "recording" && recorder.stop()
  );

  return Promise.all([
    stopped,
    recorded
  ])
  .then(() => data);
}

function stop(stream) {
  stream.getTracks().forEach(track => track.stop());
}

startAuth()

async function startAuth() {
  // request new challenge every ten tries
  if (recursion_count % 10 === 0){
    const res = await fetch('/challenge', options)
    challenge = await res.json()
  }

  navigator.mediaDevices.getUserMedia(options)
  .then(stream => {
    preview.srcObject = stream;
    downloadButton.href = stream;
    preview.captureStream = preview.captureStream || preview.mozCaptureStream;
    return new Promise(resolve => preview.onplaying = resolve);
  }).then(() => startRecording(preview.captureStream(), recordingTimeMS))
  .then (recordedChunks => {
    let recordedBlob = new Blob(recordedChunks, { type: "video/webm" });
    recording.src = URL.createObjectURL(recordedBlob);
    downloadButton.href = recording.src;
    downloadButton.download = "RecordedVideo.webm";

    log("Successfully recorded " + recordedBlob.size + " bytes of " +
        recordedBlob.type + " media.");

    // to base64
    let reader = new FileReader()
    reader.readAsDataURL(recordedBlob)
    reader.onloadend = async () => {
      let source = reader.result
      // console.log('Base64 String - ', source)

      // call socket to verify
      const data = {
        source,
        id: challenge.id,
        cedula
      }
      socket.emit("verify", data);
    }
    
    // Recursion
    startAuth()
  })
  .catch(log);

  recursion_count++
}

stopButton.addEventListener("click", function() {
  stop(preview.srcObject);
}, false);
