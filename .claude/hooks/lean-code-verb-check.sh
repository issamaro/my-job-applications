#!/usr/bin/env bash
# Lean Code — BSD 3-Clause License — Vivian Voss, 2026
# Scope: Flag forbidden function-name verb prefixes in edited Python source under services/ and routes/.

set -e

command -v jq >/dev/null || exit 0

payload=$(cat)
file=$(echo "$payload" | jq -r '.tool_input.file_path // ""')

case "$file" in
  *"/services/"*.py|*"/routes/"*.py) ;;
  *) exit 0 ;;
esac

[ -f "$file" ] || exit 0

forbidden='^(async +def|def) +(get_|load_|fetch_|acquire_|retrieve_|obtain_|save_|persist_|store_|put_|dump_|make_|build_|generate_|construct_|init_|new_|remove_|destroy_|drop_|purge_|clear_|set_|modify_|change_|patch_|mutate_|edit_|search_|query_|lookup_|locate_|filter_|select_|validate_|verify_|assert_|ensure_|test_|confirm_|convert_|transform_|deserialize_|decode_|extract_|display_|show_|print_|format_|draw_|output_|handle_|process_|manage_|do_)'

hits=$(grep -nE "$forbidden" "$file" 2>/dev/null || true)

[ -z "$hits" ] && exit 0

{
  echo "Lean Code: forbidden verb prefix in function name."
  echo "Permitted verbs only: read, write, create, delete, update, find, check, parse, render."
  echo "File: $file"
  echo "$hits"
} >&2

exit 2
