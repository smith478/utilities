<script>
    import { onMount } from 'svelte';
    
    let items = [];
    let loading = true;
    let error = null;
    
    // Form data
    let newItemName = '';
    let newItemValue = '';
    
    onMount(async () => {
      try {
        const response = await fetch('http://localhost:8000/api/items');
        const data = await response.json();
        items = data.items;
        loading = false;
      } catch (e) {
        error = e.message;
        loading = false;
      }
    });
    
    async function addItem() {
      if (!newItemName || !newItemValue) return;
      
      try {
        const response = await fetch('http://localhost:8000/api/items', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: newItemName,
            value: newItemValue
          })
        });
        
        const data = await response.json();
        items = data.items;
        
        // Reset form
        newItemName = '';
        newItemValue = '';
      } catch (e) {
        error = e.message;
      }
    }
  </script>
  
  <div class="backend-demo">
    <h2>Backend Connection Demo</h2>
    
    {#if loading}
      <p>Loading data from Python backend...</p>
    {:else if error}
      <p class="error">Error: {error}</p>
    {:else}
      <div class="items-list">
        <h3>Items from Backend:</h3>
        {#each items as item}
          <div class="item">
            <strong>{item.name}:</strong> {item.value}
          </div>
        {/each}
      </div>
    {/if}
    
    <div class="add-item-form">
      <h3>Add New Item</h3>
      <div class="form-group">
        <input type="text" bind:value={newItemName} placeholder="Item Name">
      </div>
      <div class="form-group">
        <input type="text" bind:value={newItemValue} placeholder="Item Value">
      </div>
      <button on:click={addItem}>Add Item</button>
    </div>
  </div>
  
  <style>
    .backend-demo {
      max-width: 600px;
      margin: 20px auto;
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
    }
    
    .error {
      color: red;
    }
    
    .items-list {
      margin-bottom: 20px;
    }
    
    .item {
      padding: 10px;
      margin: 5px 0;
      background-color: #f5f5f5;
      border-radius: 4px;
    }
    
    .add-item-form {
      padding-top: 15px;
      border-top: 1px solid #eee;
    }
    
    .form-group {
      margin-bottom: 10px;
    }
    
    button {
      background-color: #ff3e00;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>