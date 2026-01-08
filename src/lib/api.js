const API_BASE = '/api';

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

// Personal Info
export async function getPersonalInfo() {
  return request('/personal-info');
}

export async function updatePersonalInfo(data) {
  return request('/personal-info', {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

// Work Experiences
export async function getWorkExperiences() {
  return request('/work-experiences');
}

export async function createWorkExperience(data) {
  return request('/work-experiences', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function updateWorkExperience(id, data) {
  return request(`/work-experiences/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteWorkExperience(id) {
  return request(`/work-experiences/${id}`, {
    method: 'DELETE'
  });
}

// Education
export async function getEducation() {
  return request('/education');
}

export async function createEducation(data) {
  return request('/education', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function updateEducation(id, data) {
  return request(`/education/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteEducation(id) {
  return request(`/education/${id}`, {
    method: 'DELETE'
  });
}

// Skills
export async function getSkills() {
  return request('/skills');
}

export async function createSkills(names) {
  return request('/skills', {
    method: 'POST',
    body: JSON.stringify({ names })
  });
}

export async function deleteSkill(id) {
  return request(`/skills/${id}`, {
    method: 'DELETE'
  });
}

// Projects
export async function getProjects() {
  return request('/projects');
}

export async function createProject(data) {
  return request('/projects', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function updateProject(id, data) {
  return request(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteProject(id) {
  return request(`/projects/${id}`, {
    method: 'DELETE'
  });
}

// Languages
export async function getLanguages() {
  return request('/languages');
}

export async function createLanguage(data) {
  return request('/languages', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function updateLanguage(id, data) {
  return request(`/languages/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteLanguage(id) {
  return request(`/languages/${id}`, {
    method: 'DELETE'
  });
}

export async function reorderLanguages(items) {
  return request('/languages/reorder', {
    method: 'PUT',
    body: JSON.stringify(items)
  });
}

// Month input feature detection
export function supportsMonthInput() {
  const input = document.createElement('input');
  input.setAttribute('type', 'month');
  return input.type === 'month';
}

// Resume Generation
export async function generateResume(jobDescription, jobDescriptionId = null, language = 'en') {
  const body = { job_description: jobDescription, language };
  if (jobDescriptionId) {
    body.job_description_id = jobDescriptionId;
  }
  return request('/resumes/generate', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

export async function getResumes() {
  return request('/resumes');
}

export async function getResume(id) {
  return request(`/resumes/${id}`);
}

export async function updateResume(id, resume) {
  return request(`/resumes/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ resume })
  });
}

export async function deleteResume(id) {
  return request(`/resumes/${id}`, {
    method: 'DELETE'
  });
}

export async function getCompleteProfile() {
  return request('/profile/complete');
}

export async function downloadResumePdf(id, template = 'classic', language = 'en') {
  const response = await fetch(`${API_BASE}/resumes/${id}/pdf?template=${template}&language=${language}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'PDF generation failed' }));
    throw new Error(error.detail || 'PDF generation failed');
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;

  const disposition = response.headers.get('Content-Disposition');
  const match = disposition?.match(/filename="(.+)"/);
  a.download = match?.[1] || 'resume.pdf';

  a.click();
  URL.revokeObjectURL(url);
}

// Job Descriptions
export async function getJobDescriptions() {
  return request('/job-descriptions');
}

export async function createJobDescription(rawText) {
  return request('/job-descriptions', {
    method: 'POST',
    body: JSON.stringify({ raw_text: rawText })
  });
}

export async function getJobDescription(id) {
  return request(`/job-descriptions/${id}`);
}

export async function updateJobDescription(id, data) {
  return request(`/job-descriptions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function deleteJobDescription(id) {
  return request(`/job-descriptions/${id}`, {
    method: 'DELETE'
  });
}

export async function getJobDescriptionResumes(id) {
  return request(`/job-descriptions/${id}/resumes`);
}

export async function getJobDescriptionVersions(id) {
  return request(`/job-descriptions/${id}/versions`);
}

export async function restoreJobDescriptionVersion(jdId, versionId) {
  return request(`/job-descriptions/${jdId}/versions/${versionId}/restore`, {
    method: 'POST'
  });
}

// Photos
export async function getPhoto() {
  return request('/photos');
}

export async function uploadPhoto(imageData) {
  return request('/photos', {
    method: 'PUT',
    body: JSON.stringify({ image_data: imageData })
  });
}

export async function deletePhoto() {
  return request('/photos', {
    method: 'DELETE'
  });
}

// Profile Import
export async function importProfile(data) {
  return request('/profile/import', {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}
