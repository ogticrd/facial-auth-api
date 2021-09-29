let camera_button = document.querySelector("#start-camera")
let video = document.querySelector("#video")
let start_button = document.querySelector("#start-record")
let download_link = document.querySelector("#download-video")

let camera_stream = null
let media_recorder = null
let blobs_recorded = []

window.addEventListener('load', async function() {
  camera_stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
	video.srcObject = camera_stream
})

start_button.addEventListener('click', function() {
  media_recorder = new MediaRecorder(camera_stream, { mimeType: 'video/webm' })

  media_recorder.addEventListener('dataavailable', function(e) {
    blobs_recorded.push(e.data)
  })

  media_recorder.addEventListener('stop', function() {
    let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }))
    download_link.href = video_local
  })

  media_recorder.start(1000)

  setTimeout(() => {
    media_recorder.stop()
  }, 5000)
})