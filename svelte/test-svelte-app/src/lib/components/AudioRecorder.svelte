<script>
    let audioChunks = [];
    let recorder;
    let audioURL = '';
    let isRecording = false;
    
    async function startRecording() {
      audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream);
      
      recorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioURL = URL.createObjectURL(audioBlob);
      };
      
      recorder.start();
      isRecording = true;
    }
    
    function stopRecording() {
      if (recorder && isRecording) {
        recorder.stop();
        isRecording = false;
      }
    }
  </script>
  
  <div class="audio-recorder">
    <h2>Audio Recorder</h2>
    
    <div class="controls">
      {#if isRecording}
        <button on:click={stopRecording} class="stop">Stop Recording</button>
      {:else}
        <button on:click={startRecording} class="record">Start Recording</button>
      {/if}
    </div>
    
    {#if audioURL}
      <div class="playback">
        <h3>Playback</h3>
        <audio src={audioURL} controls></audio>
      </div>
    {/if}
  </div>
  
  <style>
    .audio-recorder {
      padding: 20px;
      background-color: #f9f9f9;
      border-radius: 8px;
      margin: 20px 0;
    }
    
    .controls {
      margin: 15px 0;
    }
    
    button {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
    }
    
    .record {
      background-color: #ff3e00;
      color: white;
    }
    
    .stop {
      background-color: #cc0000;
      color: white;
    }
    
    .playback {
      margin-top: 20px;
    }
  </style>