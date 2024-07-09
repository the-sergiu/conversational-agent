const startButton = document.getElementById('startButton');
const status = document.getElementById('status');
let ws;
let mediaRecorder;
let audioChunks = [];

function startWsConnection() {
    ws = new WebSocket('ws://127.0.0.1:8000/ws');
    ws.onopen = () => {
        console.log("Websocket connected");
    };
    ws.onmessage = (event) => {
        console.log(`This is the message: ${event.data}`)
        speakText(event.data);
    };
    ws.onerror = (event) => {
        console.error('WebSocket error:', event);
    };
    ws.onclose = () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        status.innerText = 'WebSocket disconnected.';
    };
}

const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
});

window.addEventListener("load", startWsConnection);

async function startRecording() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    let fileAsText = await toBase64(audioBlob);
                    const formData = new FormData();
                    fileAsText.replace(/^data:audio\/.+;base64,/, '');
                    console.log(fileAsText);
                    ws.send(fileAsText);
                    
                    // formData.append('file', audioBlob, 'audio.wav');
                    // fetch('http://127.0.0.1:8000/upload-audio', {
                    //     method: 'POST',
                    //     body: formData
                    // })
                    /*
                    .then(response => response.json())
                    .then(data => {
                        ws.send(data.transcript);
                    });*/
                    startButton.textContent = 'Start Continuous Recognition';
                    startButton.onclick = startRecording;
                };
                mediaRecorder.start();
                startButton.textContent = 'Recording... Click to send';
                startButton.onclick = () => mediaRecorder.stop();
            })
            .catch(error => {
                console.error(error);
                status.innerText = 'Error accessing your microphone.';
            });
    } else {
        status.innerText = 'Your browser does not support audio recording.';
    }
}

function speakText(text) {
    let speech = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(speech);
}

startButton.onclick = () => {
    startRecording();
};
