<!-- Lean Code — BSD 3-Clause License — Vivian Voss, 2026 -->
<!-- Scope: Job requirements card — skill match pills and inline experience/education rows. -->

<script>
  let { jobAnalysis = null } = $props();

  let collapsed = $state(false);
</script>

{#if jobAnalysis}
<div class="card resume-job-analysis">
  <div class="resume-job-analysis-header">
    <span class="eyebrow">JOB · REQUIREMENTS</span>
    <button
      type="button"
      class="btn-ghost resume-job-analysis-toggle"
      onclick={() => collapsed = !collapsed}
      aria-expanded={!collapsed}
    >
      {collapsed ? 'Show' : 'Hide'}
    </button>
  </div>

  {#if !collapsed}
  <div class="resume-job-analysis-body">
    {#if jobAnalysis.required_skills?.length > 0}
    <div class="resume-job-analysis-group">
      <span class="eyebrow">Required skills</span>
      <div class="resume-job-analysis-pills">
        {#each jobAnalysis.required_skills as skill}
          <span class="pill {skill.matched ? 'pill-positive' : 'pill-warn'}">
            {skill.name} {skill.matched ? '✓' : '✗'}
          </span>
        {/each}
      </div>
    </div>
    {/if}

    {#if jobAnalysis.preferred_skills?.length > 0}
    <div class="resume-job-analysis-group">
      <span class="eyebrow">Preferred skills</span>
      <div class="resume-job-analysis-pills">
        {#each jobAnalysis.preferred_skills as skill}
          <span class="pill {skill.matched ? 'pill-positive' : 'pill-warn'}">
            {skill.name} {skill.matched ? '✓' : '✗'}
          </span>
        {/each}
      </div>
    </div>
    {/if}

    {#if jobAnalysis.experience_years}
    <div class="resume-job-analysis-inline">
      <span class="resume-job-analysis-label">Experience: {jobAnalysis.experience_years.required}+ yrs</span>
      <span class="pill {jobAnalysis.experience_years.matched ? 'pill-positive' : 'pill-warn'}">
        {jobAnalysis.experience_years.matched ? '✓' : '✗'}
      </span>
    </div>
    {/if}

    {#if jobAnalysis.education}
    <div class="resume-job-analysis-inline">
      <span class="resume-job-analysis-label">Education: {jobAnalysis.education.required}</span>
      <span class="pill {jobAnalysis.education.matched ? 'pill-positive' : 'pill-warn'}">
        {jobAnalysis.education.matched ? '✓' : '✗'}
      </span>
    </div>
    {/if}
  </div>
  {/if}
</div>
{/if}

<style>
  .resume-job-analysis {
    margin: 0 0 var(--d-gap);
  }

  .resume-job-analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }

  .resume-job-analysis-toggle {
    font-size: 11px;
  }

  .resume-job-analysis-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 16px;
  }

  .resume-job-analysis-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .resume-job-analysis-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .resume-job-analysis-inline {
    display: flex;
    align-items: baseline;
    gap: 10px;
  }

  .resume-job-analysis-label {
    color: var(--ink-2);
    font-size: 13px;
  }
</style>
