<script>
    import FormElements from '$lib/components/FormElements.svelte';
    import AudioRecorder from '$lib/components/AudioRecorder.svelte';
    import AudioRecorderAdvanced from '$lib/components/AudioRecorderAdvanced.svelte';
    
    let myText = 'Edit me!';
    let myOptions = ['Svelte', 'React', 'Vue', 'Angular'];
    let mySelection = 'Svelte';
  </script>
  
  <h1>Form Components Demo</h1>
  
  <FormElements 
    textValue={myText} 
    options={myOptions} 
    selectedOption={mySelection}
  />
  
  <p>Parent component can access: Text = {myText}, Selection = {mySelection}</p>
  
  <!-- Comment out basic audio recorder -->
  <!-- <AudioRecorder /> -->
  
  <!-- Add the advanced audio recorder -->
  <AudioRecorderAdvanced />