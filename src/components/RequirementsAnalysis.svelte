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
