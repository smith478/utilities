<script>
    // Props with default values
    export let textValue = '';
    export let options = ['Option 1', 'Option 2', 'Option 3'];
    export let selectedOption = options[0];
    
    // Function to handle selection
    function handleSelect(event) {
      selectedOption = event.target.value;
    }
  </script>
  
  <div class="form-container">
    <div class="form-group">
      <label for="textbox">Editable Text Box:</label>
      <input id="textbox" type="text" bind:value={textValue} placeholder="Type something...">
      <p>Current value: {textValue}</p>
    </div>
    
    <div class="form-group">
      <label for="dropdown">Dropdown Menu:</label>
      <select id="dropdown" value={selectedOption} on:change={handleSelect}>
        {#each options as option}
          <option value={option}>{option}</option>
        {/each}
      </select>
      <p>Selected: {selectedOption}</p>
    </div>
  </div>
  
  <style>
    .form-container {
      max-width: 400px;
      margin: 20px auto;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
    }
    
    .form-group {
      margin-bottom: 15px;
    }
    
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: bold;
    }
    
    input, select {
      width: 100%;
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
  </style>