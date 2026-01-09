<script>
  let { jobAnalysis = null } = $props();

  let collapsed = $state(false);
</script>

{#if jobAnalysis}
<div class="requirements-card">
  <button
    class="requirements-header"
    onclick={() => collapsed = !collapsed}
    aria-expanded={!collapsed}
  >
    <h3>Job Requirements</h3>
    <span class="collapse-toggle">{collapsed ? '[+]' : '[-]'}</span>
  </button>

  {#if !collapsed}
  <div class="requirements-content">
    {#if jobAnalysis.required_skills?.length > 0}
    <div class="requirement-section">
      <h4>Required Skills</h4>
      <div class="skill-tags">
        {#each jobAnalysis.required_skills as skill}
          <span class="skill-tag" class:matched={skill.matched} class:unmatched={!skill.matched}>
            {skill.name} {skill.matched ? '✓' : '✗'}
          </span>
        {/each}
      </div>
    </div>
    {/if}

    {#if jobAnalysis.preferred_skills?.length > 0}
    <div class="requirement-section">
      <h4>Preferred Skills</h4>
      <div class="skill-tags">
        {#each jobAnalysis.preferred_skills as skill}
          <span class="skill-tag" class:matched={skill.matched} class:unmatched={!skill.matched}>
            {skill.name} {skill.matched ? '✓' : '✗'}
          </span>
        {/each}
      </div>
    </div>
    {/if}

    {#if jobAnalysis.experience_years}
    <div class="requirement-section requirement-inline">
      <span>Experience: {jobAnalysis.experience_years.required}+ years</span>
      <span class="match-indicator" class:matched={jobAnalysis.experience_years.matched}>
        {jobAnalysis.experience_years.matched ? '✓' : '✗'}
      </span>
    </div>
    {/if}

    {#if jobAnalysis.education}
    <div class="requirement-section requirement-inline">
      <span>Education: {jobAnalysis.education.required}</span>
      <span class="match-indicator" class:matched={jobAnalysis.education.matched}>
        {jobAnalysis.education.matched ? '✓' : '✗'}
      </span>
    </div>
    {/if}
  </div>
  {/if}
</div>
{/if}

<style>
  .requirements-card {
    border: 1px solid var(--color-border);
    border-radius: 2px;
    margin-bottom: var(--spacing-section);
  }

  .requirements-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: var(--spacing-grid);
    background: none;
    border: none;
    cursor: pointer;
    text-align: left;
    font-family: inherit;

    h3 {
      margin: 0;
    }

    &:hover {
      background: rgb(0 0 0 / 0.02);
    }

    &:focus {
      outline: 2px solid var(--color-primary);
      outline-offset: -2px;
    }
  }

  .collapse-toggle {
    font-family: monospace;
    color: rgb(var(--color-text-rgb) / 0.6);
  }

  .requirements-content {
    padding: var(--spacing-grid);
    border-top: 1px solid var(--color-border);
  }

  .requirement-section {
    margin-bottom: var(--spacing-grid);

    h4 {
      font-size: 14px;
      margin-bottom: 8px;
      font-weight: 500;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }

  .requirement-inline {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .skill-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    font-size: 14px;
    background: rgb(var(--color-primary-rgb) / 0.1);
    border: 1px solid rgb(var(--color-primary-rgb) / 0.3);
    border-radius: 2px;

    &.matched {
      color: var(--color-success);
      background: rgb(var(--color-success-rgb) / 0.1);
      border-color: rgb(var(--color-success-rgb) / 0.3);
    }

    &.unmatched {
      color: var(--color-error);
      background: rgb(var(--color-error-rgb) / 0.05);
      border-color: rgb(var(--color-error-rgb) / 0.2);
    }
  }

  .match-indicator {
    font-weight: bold;

    &.matched {
      color: var(--color-success);
    }

    &:not(.matched) {
      color: var(--color-error);
    }
  }
</style>
