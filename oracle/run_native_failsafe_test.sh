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
if ! grep -qE "tests passed|Test +#" "$OUT/build_and_run.log"; then
  fail "ctest reported no tests; TESTFILTER=failsafe selected an empty set"
fi
ran=$(grep -cE "^ *[0-9]+/[0-9]+ Test +#" "$OUT/build_and_run.log" || true)
[ "${ran:-0}" -gt 0 ] || fail "no ctest case lines in the log; the filter matched nothing"

# 5. Record the outcome as data, not as a claim.
{
  echo "ctest_target=$CTEST_NAME"
  echo "ctest_cases_run=$ran"
  echo "declared_cases=$declared"
  grep -E "tests passed|tests failed" "$OUT/build_and_run.log" | tail -2
} > "$OUT/result.txt"
echo "ORACLE RAN: $ran ctest case(s); see $OUT/result.txt"
