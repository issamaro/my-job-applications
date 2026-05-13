<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Identity card — avatar plus five-field grid bound to the shared profile store. -->

<script>
  import { store, readProfile, writeProfile } from '../lib/profileStore.svelte.js';
  import PhotoUpload from './PhotoUpload.svelte';

  let fieldErrors = $state({});
  let saveTimeout = null;

  $effect(() => {
    void readProfile();
    return () => { if (saveTimeout) clearTimeout(saveTimeout); };
  });

  function handleBlur() {
    if (!store.profile.full_name || !store.profile.email) return;
    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = setTimeout(checkAndWrite, 500);
  }

  function checkAndWrite() {
    fieldErrors = {};
    if (!store.profile.full_name.trim()) fieldErrors.full_name = 'Required';
    if (!store.profile.email.trim()) fieldErrors.email = 'Required';
    else if (!/^[^@]+@[^@]+\.[^@]+$/.test(store.profile.email))
      fieldErrors.email = 'Invalid email address';
    if (Object.keys(fieldErrors).length > 0) return;
    void writeProfile();
  }
</script>

{#if !store.loaded && !store.error}
  <div class="form">
    <div class="skeleton" style="width: 100%; height: 40px;"></div>
    <div class="skeleton" style="width: 100%; height: 40px;"></div>
    <div class="skeleton" style="width: 100%; height: 40px;"></div>
  </div>
{:else if store.error}
  <div class="form-error">{store.error}</div>
{:else}
  <div class="identity-card">
    <div class="identity-avatar" aria-hidden="true">
      <PhotoUpload bind:photo={store.profile.photo} />
    </div>
    <div class="identity-grid">
      <div class="form-row">
        <label for="full_name" class="eyebrow required">Full name</label>
        <input
          id="full_name"
          class="input"
          type="text"
          bind:value={store.profile.full_name}
          onblur={handleBlur}
          class:error={fieldErrors.full_name}
          aria-required="true"
          aria-describedby={fieldErrors.full_name ? 'full_name_error' : undefined}
        />
        {#if fieldErrors.full_name}
          <span id="full_name_error" class="error-message">{fieldErrors.full_name}</span>
        {/if}
      </div>

      <div class="form-row">
        <label for="email" class="eyebrow required">Email</label>
        <input
          id="email"
          class="input"
          type="email"
          bind:value={store.profile.email}
          onblur={handleBlur}
          class:error={fieldErrors.email}
          aria-required="true"
          aria-describedby={fieldErrors.email ? 'email_error' : undefined}
        />
        {#if fieldErrors.email}
          <span id="email_error" class="error-message">{fieldErrors.email}</span>
        {/if}
      </div>

      <div class="form-row">
        <label for="phone" class="eyebrow">Phone</label>
        <input
          id="phone"
          class="input"
          type="tel"
          bind:value={store.profile.phone}
          onblur={handleBlur}
        />
      </div>

      <div class="form-row">
        <label for="location" class="eyebrow">Location</label>
        <input
          id="location"
          class="input"
          type="text"
          bind:value={store.profile.location}
          onblur={handleBlur}
        />
      </div>

      <div class="form-row">
        <label for="linkedin_url" class="eyebrow">LinkedIn</label>
        <input
          id="linkedin_url"
          class="input"
          type="url"
          bind:value={store.profile.linkedin_url}
          onblur={handleBlur}
        />
      </div>
    </div>
  </div>
  {#if store.saved}
    <span class="saved-indicator" class:fading={!store.saving}>Saved</span>
  {/if}
{/if}

<style>
  .identity-card {
    display: flex;
    gap: 24px;
    align-items: flex-start;
  }
  .identity-avatar {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    overflow: hidden;
    background: var(--ink);
    color: var(--paper);
    flex-shrink: 0;
    display: grid;
    place-items: center;
  }
  .identity-grid {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
</style>
