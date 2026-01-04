<script>
  import { uploadPhoto, deletePhoto } from '../lib/api.js';
  import ConfirmDialog from './ConfirmDialog.svelte';
  import Toast from './Toast.svelte';

  let { photo = $bindable(null), onPhotoChange = () => {} } = $props();

  let isDragOver = $state(false);
  let showDeleteConfirm = $state(false);
  let saving = $state(false);
  let toastMessage = $state(null);
  let toastType = $state('error');

  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB

  function validateFile(file) {
    if (!ALLOWED_TYPES.includes(file.type)) {
      showToast('Please upload an image (JPEG, PNG, or WebP)', 'error');
      return false;
    }
    if (file.size > MAX_SIZE) {
      showToast('Image must be under 10MB', 'error');
      return false;
    }
    return true;
  }

  function showToast(message, type = 'error') {
    toastMessage = message;
    toastType = type;
  }

  function handleDragOver(e) {
    e.preventDefault();
    isDragOver = true;
  }

  function handleDragLeave(e) {
    e.preventDefault();
    isDragOver = false;
  }

  function handleDrop(e) {
    e.preventDefault();
    isDragOver = false;

    const file = e.dataTransfer?.files[0];
    if (file && validateFile(file)) {
      uploadFile(file);
    }
  }

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && validateFile(file)) {
      uploadFile(file);
    }
    e.target.value = '';
  }

  async function uploadFile(file) {
    saving = true;
    try {
      // Convert file to data URL for upload
      const dataUrl = await fileToDataUrl(file);
      await uploadPhoto(dataUrl);
      photo = dataUrl;
      onPhotoChange(dataUrl);
      showToast('Photo saved', 'success');
    } catch (e) {
      showToast('Could not save photo. Please try again.', 'error');
    } finally {
      saving = false;
    }
  }

  function fileToDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      document.getElementById('photo-input').click();
    }
  }

  function handleDeleteClick(e) {
    e.stopPropagation();
    showDeleteConfirm = true;
  }

  async function handleDeleteConfirm() {
    showDeleteConfirm = false;
    saving = true;

    try {
      await deletePhoto();
      photo = null;
      onPhotoChange(null);
      showToast('Photo deleted', 'success');
    } catch (e) {
      showToast('Could not delete photo. Please try again.', 'error');
    } finally {
      saving = false;
    }
  }

  function handleChangeClick(e) {
    e.stopPropagation();
    document.getElementById('photo-input').click();
  }
</script>

<div class="photo-upload-container">
  <input
    type="file"
    id="photo-input"
    accept="image/jpeg,image/png,image/webp"
    onchange={handleFileSelect}
    hidden
  />

  {#if photo}
    <!-- Has photo state -->
    <div
      class="photo-display"
      role="button"
      tabindex="0"
      aria-label="Profile photo. Press Enter to change."
      onkeydown={handleKeydown}
    >
      <img src={photo} alt="" class="photo-image" />
      <div class="photo-overlay">
        <button
          type="button"
          class="overlay-btn"
          onclick={handleChangeClick}
          disabled={saving}
        >
          Change
        </button>
        <button
          type="button"
          class="overlay-btn overlay-btn-danger"
          onclick={handleDeleteClick}
          disabled={saving}
        >
          Delete
        </button>
      </div>
    </div>
  {:else}
    <!-- Empty state -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="upload-zone"
      class:drag-over={isDragOver}
      ondragover={handleDragOver}
      ondragleave={handleDragLeave}
      ondrop={handleDrop}
      onclick={() => document.getElementById('photo-input').click()}
      onkeydown={handleKeydown}
      role="button"
      tabindex="0"
      aria-label="Upload profile photo"
    >
      <div class="upload-icon" aria-hidden="true">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
          <circle cx="12" cy="13" r="4"></circle>
        </svg>
      </div>
      {#if isDragOver}
        <span class="upload-text" aria-live="polite">Drop to upload</span>
      {:else}
        <span class="upload-text">Add profile photo</span>
        <span class="upload-hint">Drag or click</span>
      {/if}
    </div>
  {/if}

  {#if saving}
    <div class="saving-overlay">
      <div class="spinner"></div>
    </div>
  {/if}
</div>

{#if showDeleteConfirm}
  <ConfirmDialog
    message="Delete your profile photo?"
    onConfirm={handleDeleteConfirm}
    onCancel={() => showDeleteConfirm = false}
  />
{/if}

<Toast bind:message={toastMessage} type={toastType} />

<style>
  .photo-upload-container {
    position: relative;
    width: 120px;
    height: 120px;
    flex-shrink: 0;
  }

  .upload-zone {
    width: 120px;
    height: 120px;
    border: 2px dashed #ccc;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: border-color 0.2s, background-color 0.2s;
    background: #fafafa;
  }

  .upload-zone:hover,
  .upload-zone:focus {
    border-color: #666;
    outline: none;
  }

  .upload-zone:focus {
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
  }

  .upload-zone.drag-over {
    border-color: #333;
    border-style: solid;
    background: #f0f0f0;
  }

  .upload-icon {
    color: #999;
    margin-bottom: 4px;
  }

  .upload-text {
    font-size: 12px;
    color: #666;
    text-align: center;
  }

  .upload-hint {
    font-size: 10px;
    color: #999;
    margin-top: 2px;
  }

  .photo-display {
    position: relative;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    overflow: hidden;
  }

  .photo-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .photo-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    opacity: 0;
    transition: opacity 0.2s;
  }

  .photo-display:hover .photo-overlay,
  .photo-display:focus-within .photo-overlay {
    opacity: 1;
  }

  .overlay-btn {
    padding: 6px 12px;
    font-size: 12px;
    background: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    min-width: 70px;
  }

  .overlay-btn:hover {
    background: #f0f0f0;
  }

  .overlay-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .overlay-btn-danger {
    background: #cc0000;
    color: white;
  }

  .overlay-btn-danger:hover {
    background: #aa0000;
  }

  .saving-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid #ccc;
    border-top-color: #333;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
