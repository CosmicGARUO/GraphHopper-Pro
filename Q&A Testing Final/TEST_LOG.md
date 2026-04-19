# Q&A Testing Log - UI Enhanced Version

**Tester:** Arlindo B. Mayor Jr.
**Date:** 2026-04-19
**Branch:** `feature-ui-styling`

## Test Results

| Test Case            | Interaction Steps         | Expected Outcome                                          | Result              |
| :------------------- | :------------------------ | :-------------------------------------------------------- | :------------------ |
| **Invalid Location** | Enter "Asdfghjkl"         | **Red** error message displayed; system remains stable.   | [ ] Pass / [ ] Fail |
| **Empty Input**      | Press Enter (no input)    | **Red** error prompt appears; asks to re-enter.           | [ ] Pass / [ ] Fail |
| **Unit Toggle**      | Choose option "2" (Miles) | Summary and Directions table display units as "mi".       | [ ] Pass / [ ] Fail |
| **Quit Command**     | Type "q"                  | Program terminates cleanly after color-styled UI closing. | [ ] Pass / [ ] Fail |

## UI/UX Visual Verification

- [ ] **Colors:** Verify that the "ROUTE SUMMARY" is in Magenta and target locations are in Cyan.
- [ ] **Tables:** Verify that "Turn-by-turn Directions" is rendered within a `fancy_grid` table using `tabulate`.
