let isVideoPlaying = false;
let cedulaValue = ''
let blobs_recorded = []
let capture = null
let predictions = []
let recorder = null
let p = null
let challenge = null

function videoLoad() {
  video.loop();
  capture.hide();
  button.hide();
  isVideoPlaying = true;
}

function toggleRecording(){
  if (recorder.state != 'recording' && cedulaValue.length === 11){
    recorder.start();
    facemesh.on("predict", results => {
      predictions = results;
    })
    setTimeout(async () => {
      recorder.stop()
    }, 5000)
  } else {
    alert('Put you cedula on the input cedula')
  }
}

// function draw() {

// }

async function setup() {
  createCanvas(640, 480)
  p = createP('1. Enter cedula number in the box below.')
  let cedulaInput = createInput()
  let button = createButton("Sign in")
  // handles
  button.mousePressed(toggleRecording)
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
      blobs_recorded.push(e.data)
    })
    
    recorder.addEventListener('stop', function() {
      let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }))
      console.log(video_local)
  
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
          p.html('3. Verifying...')
          const res = await fetch('/verify', options)
          const result = await res.json()
          console.log(result)
          facemesh.on("predict", results => {
            predictions = [];
          })
          cedulaValue = ''
          if (result.verified){
            console.log('Working')
            p.html('4. Verified Successfully!')
          }else {
            p.html('4. Not Verified!')
          }
        }
      } else{
        alert('Put you cedula on the input cedula')
      }
      blobs_recorded = []
    })
  });
  capture.hide()
  facemesh = ml5.facemesh(capture, modelReady)
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

function modelReady() {
  console.log("Model ready!");
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
  console.log(cedulaValue)
}
