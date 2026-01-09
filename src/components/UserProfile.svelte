<script>
  import { getUser, updateUser } from '../lib/api.js';
  import PhotoUpload from './PhotoUpload.svelte';

  let data = $state({
    full_name: '',
    email: '',
    phone: '',
    location: '',
    linkedin_url: '',
    summary: '',
    photo: null
  });
  let loading = $state(true);
  let saving = $state(false);
  let saved = $state(false);
  let error = $state(null);
  let fieldErrors = $state({});
  let saveTimeout = null;
  let savedTimeout = null;

  $effect(() => {
    loadData();
    return () => {
      if (saveTimeout) clearTimeout(saveTimeout);
      if (savedTimeout) clearTimeout(savedTimeout);
    };
  });

  async function loadData() {
    try {
      loading = true;
      const result = await getUser();
      if (result) {
        data = { ...data, ...result };
      }
    } catch (e) {
      error = 'Could not load profile. Please refresh.';
    } finally {
      loading = false;
    }
  }

  function handleBlur() {
    if (!data.full_name || !data.email) return;

    if (saveTimeout) clearTimeout(saveTimeout);
    saveTimeout = setTimeout(save, 500);
  }

  async function save() {
    fieldErrors = {};

    if (!data.full_name.trim()) {
      fieldErrors.full_name = 'Required';
    }
    if (!data.email.trim()) {
      fieldErrors.email = 'Required';
    } else if (!/^[^@]+@[^@]+\.[^@]+$/.test(data.email)) {
      fieldErrors.email = 'Invalid email address';
    }

    if (Object.keys(fieldErrors).length > 0) return;

    try {
      saving = true;
      await updateUser(data);
      saved = true;
      if (savedTimeout) clearTimeout(savedTimeout);
      savedTimeout = setTimeout(() => { saved = false; }, 2000);
    } catch (e) {
      error = 'Could not save. Please try again.';
    } finally {
      saving = false;
    }
  }
</script>

{#if loading}
  <div class="form">
    <div class="skeleton" style="width: 100%; height: 40px;"></div>
    <div class="skeleton" style="width: 100%; height: 40px;"></div>
    <div class="skeleton" style="width: 100%; height: 40px;"></div>
  </div>
{:else}
  {#if error}
    <div class="form-error">{error}</div>
  {/if}

  <div class="personal-info-layout">
    <PhotoUpload bind:photo={data.photo} />

    <form class="form personal-info-form" onsubmit={(e) => e.preventDefault()}>
    <div class="form-row">
      <label for="full_name" class="required">Name</label>
      <input
        id="full_name"
        type="text"
        bind:value={data.full_name}
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
      <label for="email" class="required">Email</label>
      <input
        id="email"
        type="email"
        bind:value={data.email}
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
      <label for="phone">Phone</label>
      <input
        id="phone"
        type="tel"
        bind:value={data.phone}
        onblur={handleBlur}
      />
    </div>

    <div class="form-row">
      <label for="location">Location</label>
      <input
        id="location"
        type="text"
        bind:value={data.location}
        onblur={handleBlur}
      />
    </div>

    <div class="form-row">
      <label for="linkedin_url">LinkedIn</label>
      <input
        id="linkedin_url"
        type="url"
        bind:value={data.linkedin_url}
        onblur={handleBlur}
      />
    </div>

    <div class="form-row">
      <label for="summary">Summary</label>
      <textarea
        id="summary"
        bind:value={data.summary}
        onblur={handleBlur}
      ></textarea>
    </div>

    {#if saved}
      <span class="saved-indicator" class:fading={!saving}>Saved</span>
    {/if}
    </form>
  </div>
{/if}

<style>
  .personal-info-layout {
    display: flex;
    gap: 24px;
    align-items: flex-start;
  }

  .personal-info-form {
    flex: 1;
  }

  @media (max-width: 600px) {
    .personal-info-layout {
      flex-direction: column;
      align-items: center;
    }
  }
</style>
