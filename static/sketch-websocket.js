let isVideoPlaying = false;
let cedulaValue = ''
let blobs_recorded = []
let capture = null
let predictions = []
let recorder = null
let p = null 
let challenge = null

async function setup() {
  const ws = new WebSocket("ws://localhost:8000/verify")
  ws.onmessage = function(event) {
      console.log(event.data)
  }

  createCanvas(640, 480)
  p = createP('1. Enter cedula number in the box below.')
  let cedulaInput = createInput()
  let button = createButton("Sign in")
  // handles
  // button.mousePressed(toggleRecording)
  cedulaInput.input(updateCedulaValue)

  var constraints = {
    video: {
      mandatory: {
        minWidth: 640,
        minHeight: 480,
        echoCancellation: true,
      },
      optional: [{ maxFrameRate: 30}],
    },
    audio: false 
  };
  capture = createCapture(constraints, function(stream)   {    
    recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });

    recorder.addEventListener('dataavailable', function(e) {
      if (cedulaValue.length === 11){
        let reader = new FileReader()
        reader.readAsDataURL(new Blob([e.data], { type: 'video/webm' }))
        reader.onloadend = async () => {
          let base64String = reader.result
          console.log('Base64 String - ', base64String)
          ws.send(JSON.stringify({"source": base64String, "id": challenge.id}))
        }
      }
    })
    
    recorder.addEventListener('start', function() {
      setInterval(() => {
        recorder.requestData()
      }, 500)
    })

    recorder.start()
  })
  capture.hide()
  const options = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  }
  const res = await fetch('/challenge', options)
  challenge = await res.json()
  console.log(challenge)
}

function draw(){
  if (cedulaValue.length === 11){
    p.html('2. Push Sign in to start authentication process.')
  }
  image(capture, 0, 0, width, height)
  drawKeypoints()
}

function drawKeypoints() {
  for (let i = 0; i < predictions.length; i += 1) {
    const keypoints = predictions[i].scaledMesh;
    stroke(255, 255, 255, 70)
    strokeWeight(4);

    for (let j = 0; j < keypoints.length; j += 1) {
      const [x, y] = keypoints[j];
      
      const ram = Math.floor(Math.random() * 2)
      if (ram == 0){
        point(x, y)
      }
    }
  }
}

function updateCedulaValue(event){
  cedulaValue = this.value()
}
