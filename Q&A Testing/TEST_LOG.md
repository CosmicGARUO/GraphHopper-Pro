# Q&A Testing Log

**Tester:** Arlindo B. Mayor Jr.
**Date:** 2026-04-19
**Branch:** `feature-logic-units`

## Test Results

| Test Case            | Interaction Steps                                                    | Expected Outcome                                         | Result              |
| :------------------- | :------------------------------------------------------------------- | :------------------------------------------------------- | :------------------ |
| **Invalid Location** | Enter "Asdfghjkl" (or any non-existent location) in the input field. | The program should display an error/warning message.     | [ ] Pass / [ ] Fail |
| **Empty Input**      | Press Enter without typing anything.                                 | The program should prompt you to re-enter a valid input. | [ ] Pass / [ ] Fail |
| **Unit Toggle**      | Choose option "2" during the unit selection phase.                   | The output should successfully toggle to display miles.  | [ ] Pass / [ ] Fail |
| **Quit Command**     | Type "q" and press Enter.                                            | The program should terminate the process cleanly.        | [ ] Pass / [ ] Fail |

---

## Step-by-Step Execution Procedure

Follow these steps to validate your implementation in `graphhopper_parse-json_7.py`:

### 1. Invalid Location Testing

- **Procedure:** Run the script, select a vehicle, and at the `Starting Location:` prompt, enter `Asdfghjkl`.
- **Logic Check:** The code hits the `else` block when `json_status` is not 200, triggering the error output.

### 2. Empty Input Testing

- **Procedure:** When prompted for a location, press **Enter** without typing text.
- **Logic Check:** The `while location == "":` loop will catch the empty string and re-prompt you with "Enter the location again:".

### 3. Unit Toggle Testing

- **Procedure:** Restart the script and select `2` at the "Select preferred units" prompt.
- **Logic Check:** The script sets `use_miles = True`, which updates the formatting for both total distance and route instructions.

### 4. Quit Command Testing

- **Procedure:** At any prompt (Vehicle, Start, or Destination), type `q` or `quit` and press **Enter**.
- **Logic Check:** The `if` statements check for these specific inputs and trigger a `break` to exit the `while True` loop.

---
