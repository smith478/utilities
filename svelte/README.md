# Setting Up Svelte

1. Prerequisites: Ensure you have Node.js installed
- Check if installed: `node -v`
- If not, download from [nodejs.org](nodejs.org)

2. Create a new Svelte project:
```bash
# Install the SvelteKit template
npx sv create test-svelte-app

# Navigate to your project
cd test-svelte-app

# Start the development server
npm run dev -- --open
```

# Learning Path: From Basics to Backend Integration

## Exercise 1: Hello World Component
Create your first component in `src/routes/+page.svelte`:
```svelte
<script>
  let name = 'World';
</script>

<h1>Hello {name}!</h1>

<input bind:value={name} placeholder="Enter your name">

<style>
  h1 {
    color: #ff3e00;
  }
</style>
```

## Exercise 2: Building UI Components
Create a new file `src/lib/components/FormElements.svelte`:
```svelte
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
```

Now use this component in `src/routes/+page.svelte`:
```svelte
<script>
  import FormElements from '$lib/components/FormElements.svelte';
  
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
```
