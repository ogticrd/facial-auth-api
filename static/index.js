let camera_button = document.querySelector("#start-camera")
let video = document.querySelector("#video")
let start_button = document.querySelector("#start-record")
let download_link = document.querySelector("#download-video")
let cedulaInput = document.querySelector("#cedulaInput")

let camera_stream = null
let media_recorder = null
let blobs_recorded = []
let cedulaValue = ''

let challenge = null

window.addEventListener('load', async function() {
  camera_stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
	video.srcObject = camera_stream
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  }
  const res = await fetch('/challenge', options)
  challenge = await res.json()
  console.log(challenge)
})

cedulaInput.addEventListener('input', updateCedulaValue)

start_button.addEventListener('click', function() {
  if (cedulaValue.length !== 11){
    alert('Put you cedula on the field cedula and must have 11 character')
    return
  }
  media_recorder = new MediaRecorder(camera_stream, { mimeType: 'video/webm' })

  media_recorder.addEventListener('dataavailable', function(e) {
    blobs_recorded.push(e.data)
  })

  media_recorder.addEventListener('stop', function() {
    let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }))
    console.log(video_local)
    download_link.href = video_local

    // Send base64 to api
    if (cedulaValue.length === 11){
      let reader = new FileReader()
      reader.readAsDataURL(new Blob(blobs_recorded, { type: 'video/webm' }))
      reader.onloadend = async () => {
        let base64String = reader.result
        console.log('Base64 String - ', base64String)

        const data = {
          data: {
            cedula: cedulaValue,
            source: base64String,
            id: challenge.id
          }
        }
        const options = {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        }
        const res = await fetch('/verify', options)
        const result = await res.json()
        console.log(result) 
      }
    } else{
      alert('Put you cedula on the field cedula')
    }

    blobs_recorded = []
  })

  media_recorder.start(1000)

  setTimeout(async () => {
    media_recorder.stop()
  }, 5000)
})

function updateCedulaValue(event){
  cedulaValue = event.target.value
  console.log(cedulaValue)
}