// Lean Code — BSD 3-Clause License — Vivian Voss, 2026
// Scope: Shared profile state — load, save, initials helper.

import { getUser, updateUser } from './api.js';

export const store = $state({
  profile: {
    full_name: '',
    email: '',
    phone: '',
    location: '',
    linkedin_url: '',
    summary: '',
    photo: null,
  },
  loaded: false,
  saving: false,
  saved: false,
  error: null,
  saveError: null,
});

let _pending = null;
let _savedTimeout = null;

export function parseInitials(fullName) {
  const tokens = (fullName ?? '').trim().split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return '??';
  if (tokens.length === 1) return tokens[0][0].toUpperCase();
  return (tokens[0][0] + tokens[tokens.length - 1][0]).toUpperCase();
}

export function readInitials() {
  return parseInitials(store.profile.full_name);
}

export async function readProfile() {
  if (store.loaded) return;
  if (_pending) return _pending;

  _pending = (async () => {
    try {
      const result = await getUser();
      if (result) Object.assign(store.profile, result);
      store.loaded = true;
      store.error = null;
    } catch (e) {
      store.error = 'Could not load profile. Please refresh.';
    } finally {
      _pending = null;
    }
  })();

  return _pending;
}

export async function writeProfile() {
  try {
    store.saving = true;
    await updateUser(store.profile);
    store.saved = true;
    store.saveError = null;
    if (_savedTimeout) clearTimeout(_savedTimeout);
    _savedTimeout = setTimeout(() => { store.saved = false; }, 2000);
  } catch (e) {
    store.saveError = 'Could not save. Please try again.';
  } finally {
    store.saving = false;
  }
}
