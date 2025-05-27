<script>
    import FormElements from '$lib/components/FormElements.svelte';
    import AudioRecorder from '$lib/components/AudioRecorder.svelte';
    import AudioRecorderAdvanced from '$lib/components/AudioRecorderAdvanced.svelte';
    
    let myText = 'Edit me!';
    let myOptions = ['Svelte', 'React', 'Vue', 'Angular'];
    let mySelection = 'Svelte';
    
    // Dark mode state
    let isDarkMode = false;
    
    // Toggle dark mode function
    function toggleDarkMode() {
        isDarkMode = !isDarkMode;
        // Apply dark mode class to document body
        if (typeof document !== 'undefined') {
            document.body.classList.toggle('dark-mode', isDarkMode);
        }
    }
    
    // Initialize dark mode on component mount
    import { onMount } from 'svelte';
    onMount(() => {
        // Check for saved preference or default to light mode
        const savedMode = localStorage.getItem('darkMode');
        if (savedMode === 'true') {
            isDarkMode = true;
            document.body.classList.add('dark-mode');
        }
    });
    
    // Save preference when it changes
    $: if (typeof localStorage !== 'undefined') {
        localStorage.setItem('darkMode', isDarkMode.toString());
    }
</script>

<div class="page-container">
    <!-- Header with dark mode toggle -->
    <header class="page-header">
        <h1>Form Components Demo</h1>
        <button 
            class="dark-mode-toggle" 
            on:click={toggleDarkMode}
            aria-label="Toggle dark mode"
        >
            {#if isDarkMode}
                ☀️ Light
            {:else}
                🌙 Dark
            {/if}
        </button>
    </header>
    
    <main>
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
    </main>
</div>

<style>
    .page-container {
        min-height: 100vh;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        border-bottom: 1px solid var(--border-color, #e2e8f0);
    }
    
    .page-header h1 {
        margin: 0;
        font-size: 1.5rem;
    }
    
    .dark-mode-toggle {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--button-bg, #f8f9fa);
        border: 1px solid var(--border-color, #e2e8f0);
        border-radius: 0.5rem;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }
    
    .dark-mode-toggle:hover {
        background: var(--button-hover-bg, #e9ecef);
        transform: translateY(-1px);
    }
    
    main {
        padding: 2rem;
    }
    
    /* Light mode (default) */
    :global(body) {
        --bg-color: #ffffff;
        --text-color: #1a202c;
        --border-color: #e2e8f0;
        --button-bg: #f8f9fa;
        --button-hover-bg: #e9ecef;
        background-color: var(--bg-color);
        color: var(--text-color);
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
    /* Dark mode */
    :global(body.dark-mode) {
        --bg-color: #1a202c;
        --text-color: #f7fafc;
        --border-color: #4a5568;
        --button-bg: #2d3748;
        --button-hover-bg: #4a5568;
        background-color: var(--bg-color);
        color: var(--text-color);
    }
    
    :global(body.dark-mode) .page-header {
        border-bottom-color: var(--border-color);
    }
</style>