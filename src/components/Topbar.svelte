<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Editorial Topbar shell — wordmark, primary nav, search pill, user mark. -->

<script>
  let { activeTab, onTabChange } = $props();

  const slots = [
    { id: 'dashboard', label: 'Dashboard',      tab: null },
    { id: 'pipeline',  label: 'Pipeline',       tab: null },
    { id: 'jobs',      label: 'Saved jobs',     tab: null },
    { id: 'profile',   label: 'Profile',        tab: 'profile' },
    { id: 'tailor',    label: 'Tailor CV',      tab: 'resume' },
    { id: 'interview', label: 'Interview prep', tab: null },
  ];

  const activeSlotId = $derived(slots.find(s => s.tab === activeTab)?.id);
</script>

<header class="topbar" role="banner">
  <div class="topbar-wordmark">
    <span class="topbar-wordmark-italic">my</span><span class="topbar-wordmark-roman">CV</span><span class="topbar-wordmark-dot" aria-hidden="true"></span>
  </div>

  <nav class="topbar-nav" aria-label="Primary">
    {#each slots as slot (slot.id)}
      {@const isActive = slot.id === activeSlotId}
      {@const isDisabled = slot.tab === null}
      <button
        type="button"
        class="topbar-slot"
        class:active={isActive}
        class:disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-current={isActive ? 'page' : undefined}
        tabindex={isDisabled ? -1 : 0}
        data-slot-id={slot.id}
        onclick={() => { if (slot.tab) onTabChange(slot.tab); }}
      >{slot.label}</button>
    {/each}
  </nav>

  <div class="topbar-right">
    <div class="topbar-search" aria-hidden="true">
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4">
        <circle cx="7" cy="7" r="4.5"/>
        <path d="M11 11l3 3"/>
      </svg>
      <span>Find a job, resume…</span>
      <span class="topbar-search-kbd num">⌘K</span>
    </div>
    <div class="topbar-user" aria-hidden="true">LM</div>
  </div>
</header>

<style>
  .topbar {
    height: 64px;
    padding: 0 32px;
    border-bottom: 1px solid var(--rule);
    background: var(--paper);
    display: flex;
    align-items: center;
    gap: 36px;
    flex-shrink: 0;
  }

  .topbar-wordmark {
    display: flex;
    align-items: baseline;
    gap: 0;
    font-family: var(--font-display);
    font-size: 22px;
    line-height: 1;
    color: var(--ink);
  }
  .topbar-wordmark-italic {
    font-style: italic;
    font-weight: 400;
  }
  .topbar-wordmark-roman {
    font-weight: 600;
    letter-spacing: -0.01em;
  }
  .topbar-wordmark-dot {
    display: inline-block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--accent);
    margin-left: 4px;
    transform: translateY(-2px);
  }

  .topbar-nav {
    display: flex;
    gap: 4px;
    flex: 1;
    height: 100%;
    align-items: stretch;
  }

  .topbar-slot {
    padding: 20px 12px;
    font-family: var(--font-ui);
    font-size: 13px;
    font-weight: 400;
    color: var(--ink-3);
    background: transparent;
    border: 0;
    border-bottom: 1px solid transparent;
    margin-bottom: -1px;
    cursor: pointer;
    line-height: 1;
  }
  .topbar-slot:hover:not(.disabled):not(.active) {
    color: var(--ink-2);
  }
  .topbar-slot:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: -4px;
  }
  .topbar-slot.active {
    color: var(--ink);
    font-weight: 500;
    border-bottom-color: var(--ink);
  }
  .topbar-slot.disabled {
    color: var(--ink-4);
    cursor: not-allowed;
    pointer-events: none;
  }

  .topbar-right {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .topbar-search {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: var(--paper-2);
    border: 1px solid var(--rule);
    border-radius: var(--r-sm);
    color: var(--ink-3);
    font-size: 12px;
    min-width: 200px;
  }
  .topbar-search-kbd {
    margin-left: auto;
    font-size: 10px;
    padding: 1px 4px;
    border: 1px solid var(--rule);
    border-radius: 2px;
  }

  .topbar-user {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--ink);
    color: var(--paper);
    display: grid;
    place-items: center;
    font-family: var(--font-display);
    font-size: 14px;
    font-style: italic;
  }
</style>
