const startButton = document.getElementById('startButton');
const status = document.getElementById('status');
let ws;
let mediaRecorder;
let audioChunks = [];

function startRecording() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('file', audioBlob, 'audio.wav');
                    fetch('http://127.0.0.1:8000/upload-audio', {
                        method: 'POST',
                        body: formData
                    }).then(response => response.json())
                    .then(data => {
                        ws.send(data.transcript);
                    });
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
    ws = new WebSocket('ws://127.0.0.1:8000/ws');
    ws.onopen = () => {
        startRecording();
    };
    ws.onmessage = (event) => {
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
};
