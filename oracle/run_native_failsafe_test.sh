#!/usr/bin/env bash
# Build and run PX4's OWN failsafe unit test against the pinned firmware, and record what actually happened.
#
#   oracle/run_native_failsafe_test.sh <px4 checkout> <output dir>
#
# This is layer B of the three-layer differential (critique 2026-09-24, F4): the real C++ Failsafe class on the
# same inputs as the hand-derived model and the integrated runtime. It is NOT an independent safety oracle,
# because it is the implementation under study.
#
# Names here are read from the pinned source, not from today's upstream documentation:
#   src/modules/commander/failsafe/CMakeLists.txt  px4_add_functional_gtest(SRC failsafe_test.cpp ...)
#   cmake/px4_add_gtest.cmake                      TESTNAME = functional-<file with "Test" stripped>
#   Makefile `tests:` target                       builds px4_sitl_test and passes TESTFILTER to ctest -R
# Verify them again if the pin moves.
set -euo pipefail

PX4="${1:?usage: run_native_failsafe_test.sh <px4 checkout> <output dir>}"
OUT="${2:?usage: run_native_failsafe_test.sh <px4 checkout> <output dir>}"
EXPECTED_COMMIT="d6f12ad1c4f70ad3230afd7d86e971421e02fef4"
CTEST_NAME="functional-failsafe_test"
mkdir -p "$OUT"

fail() { echo "ORACLE BLOCKED: $*" >&2; echo "$*" > "$OUT/blocked.txt"; exit 1; }

# 1. Identity first. A result without a recorded environment is not evidence.
commit="$(git -C "$PX4" rev-parse HEAD)"
[ "$commit" = "$EXPECTED_COMMIT" ] || fail "checkout is $commit, not the pinned $EXPECTED_COMMIT"
{
  echo "px4_commit=$commit"
  echo "px4_describe=$(git -C "$PX4" describe --tags --always)"
  echo "uname=$(uname -srm)"
  echo "cxx=$(${CXX:-c++} --version | head -1)"
  echo "cmake=$(cmake --version | head -1)"
  echo "recorded_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT/environment.txt"
git -C "$PX4" submodule status --recursive > "$OUT/submodules.txt" 2>&1 || true

# 2. Confirm the target exists in THIS source before building anything.
grep -q "failsafe_test.cpp" "$PX4/src/modules/commander/failsafe/CMakeLists.txt" \
  || fail "the pinned source does not register failsafe_test.cpp; re-read the CMakeLists before assuming a name"
grep -oE "^TEST_F\(FailsafeTest, [A-Za-z0-9_]+\)" "$PX4/src/modules/commander/failsafe/failsafe_test.cpp" \
  | sed 's/.*, //; s/)//' > "$OUT/declared_cases.txt"
declared=$(wc -l < "$OUT/declared_cases.txt" | tr -d ' ')
[ "$declared" -gt 0 ] || fail "no TEST_F cases found in failsafe_test.cpp"
echo "declared_cases=$declared" >> "$OUT/environment.txt"

# 3. Build only the test target. A build failure is an environment result, not a PX4 result.
if ! make -C "$PX4" tests TESTFILTER=failsafe > "$OUT/build_and_run.log" 2>&1; then
  tail -60 "$OUT/build_and_run.log" > "$OUT/tail.log"
  fail "build or test run failed; see build_and_run.log. This is an ENVIRONMENT result: it says nothing about PX4's behaviour."
fi

# 4. A filter that selected nothing is a failure, not a pass.
ctest_entries=$(grep -cE "^ *[0-9]+/[0-9]+ Test +#" "$OUT/build_and_run.log" || true)
[ "${ctest_entries:-0}" -gt 0 ] || fail "no ctest case lines in the log; TESTFILTER=failsafe matched nothing"

# 5. ctest runs the whole gtest binary as ONE entry and hides its output on success, so "1/1 Test passed" in
#    0.00 s is NOT evidence that the nine cases ran. Run the binary directly and count what it reports.
#    The first oracle dispatch (run 36221992524) was green on the ctest line alone and proved nothing.
binary=$(find "$PX4/build/px4_sitl_test" -type f -name "$CTEST_NAME" -perm -u+x 2>/dev/null | head -1)
[ -n "$binary" ] || fail "built $CTEST_NAME but cannot find its executable under build/px4_sitl_test"
echo "gtest_binary=$binary" >> "$OUT/environment.txt"
echo "gtest_binary_sha256=$(sha256sum "$binary" | cut -d" " -f1)" >> "$OUT/environment.txt"

"$binary" --gtest_list_tests > "$OUT/gtest_listed.txt" 2>&1 \
  || fail "the test binary could not even list its cases"
listed=$(grep -cE "^  [A-Za-z0-9_]+" "$OUT/gtest_listed.txt" || true)
[ "${listed:-0}" -eq "$declared" ] \
  || fail "the binary lists $listed cases but the source declares $declared; the filter or the build is wrong"

# PX4 warns that repeated setup in one process may not clean up fully, so run each case in its own process.
passed=0
: > "$OUT/gtest_per_case.log"
while read -r case_name; do
  [ -n "$case_name" ] || continue
  if "$binary" --gtest_filter="FailsafeTest.$case_name" >> "$OUT/gtest_per_case.log" 2>&1; then
    passed=$((passed + 1))
    echo "PASS FailsafeTest.$case_name" >> "$OUT/per_case_result.txt"
  else
    echo "FAIL FailsafeTest.$case_name" >> "$OUT/per_case_result.txt"
  fi
done < "$OUT/declared_cases.txt"

# 6. Record the outcome as data, not as a claim.
{
  echo "ctest_target=$CTEST_NAME"
  echo "ctest_entries=$ctest_entries"
  echo "declared_cases=$declared"
  echo "listed_by_binary=$listed"
  echo "cases_run_in_own_process=$declared"
  echo "cases_passed=$passed"
  grep -E "tests passed|tests failed" "$OUT/build_and_run.log" | tail -2
} > "$OUT/result.txt"
[ "$passed" -eq "$declared" ] \
  || fail "$passed of $declared cases passed; see per_case_result.txt. This is a PX4 result, not an environment one."
echo "ORACLE RAN: $passed/$declared gtest cases passed, each in its own process; see $OUT/result.txt"
