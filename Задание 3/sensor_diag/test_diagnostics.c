#include <stdio.h>
#include <assert.h>
#include "diagnostics.h"

#define PASS(msg) printf("PASS: %s\n", (msg))

static void test_init(void) {
    DiagChannel ch;
    diag_init(&ch);
    assert(ch.calibrated == 0);
    assert(ch.calib_count == 0);
    assert(ch.calib_mean == 0.0);
    assert(ch.calib_m2 == 0.0);
    assert(ch.calib_std == 0.0);
    assert(ch.ewma == 0.0);
    assert(ch.cusum_pos == 0.0);
    assert(ch.cusum_neg == 0.0);
    assert(ch.has_prev == 0);
    assert(ch.win_idx == 0);
    assert(ch.win_full == 0);
    PASS("diag_init zeroes all fields");
}

static void test_calibration(void) {
    DiagChannel ch;
    int i, flag;
    diag_init(&ch);

    /* Подаём 250 значений: синусоида mean=50, ampl=2 */
    for (i = 0; i < DIAG_CALIB_SAMPLES; i++) {
        double v = 50.0 + 2.0 * (((i % 10) - 5) * 0.2);
        flag = diag_process(&ch, v);
        assert(flag == DIAG_FLAG_GOOD);
    }
    assert(ch.calibrated == 1);
    assert(ch.calib_mean > 49.0 && ch.calib_mean < 51.0);
    assert(ch.calib_std > 0.0);
    PASS("calibration computes mean and std");
}

static void test_calibration_outlier_rejection(void) {
    DiagChannel ch;
    int i;
    diag_init(&ch);

    for (i = 0; i < DIAG_CALIB_SAMPLES - 1; i++) {
        diag_process(&ch, 50.0);
    }
    /* Выброс — не должен войти в статистику */
    diag_process(&ch, 50000.0);

    assert(ch.calib_mean > 49.5 && ch.calib_mean < 50.5);
    PASS("calibration rejects outliers > 3 sigma");
}

static void calibrate(DiagChannel *ch, double mean) {
    int i;
    for (i = 0; i < DIAG_CALIB_SAMPLES; i++) {
        diag_process(ch, mean);
    }
}

static void test_rate_detector(void) {
    DiagChannel ch;
    int flag;
    diag_init(&ch);
    calibrate(&ch, 50.0);

    flag = diag_process(&ch, 50.1);
    assert(flag == DIAG_FLAG_GOOD);
    PASS("rate detector: small change -> Good");

    flag = diag_process(&ch, 50.1 + 100.0 * ch.calib_std);
    assert(flag == DIAG_FLAG_BAD);
    PASS("rate detector: large spike -> Bad");
}

static void test_variance_detector(void) {
    DiagChannel ch;
    int flag, i;
    diag_init(&ch);
    calibrate(&ch, 50.0);

    /* Нормальный сигнал */
    for (i = 0; i < DIAG_WINDOW; i++) {
        double v = 50.0 + (i % 2 == 0 ? 0.05 : -0.05) * ch.calib_std;
        flag = diag_process(&ch, v);
    }
    assert(flag == DIAG_FLAG_GOOD);
    PASS("variance detector: normal variance -> Good");

    /* Залипший сигнал */
    diag_init(&ch);
    calibrate(&ch, 50.0);
    for (i = 0; i < DIAG_WINDOW; i++) {
        flag = diag_process(&ch, 50.0);
    }
    assert(flag == DIAG_FLAG_BAD);
    PASS("variance detector: frozen signal -> Bad");
}

static void test_cusum_detector(void) {
    DiagChannel ch;
    int flag, i;
    diag_init(&ch);
    calibrate(&ch, 50.0);

    /* A large sudden shift (20x std) triggers CUSUM before ref_mean adapts.
       ref_mean lag ~50 steps, so cusum accumulates fast in first 10-20 steps. */
    flag = DIAG_FLAG_GOOD;
    for (i = 0; i < 20; i++) {
        flag = diag_process(&ch, 50.0 + 20.0 * ch.calib_std);
    }
    assert(flag == DIAG_FLAG_POTENTIAL || flag == DIAG_FLAG_BAD);
    PASS("CUSUM detector: large sustained shift -> Potential or Bad");

    /* Recovery: feed normal oscillating signal for long enough.
       ref_mean adapts back in ~500 steps (α=0.02), CUSUM decays once
       diff returns near zero.  Constant input would be flagged as frozen,
       so use small alternating noise well within normal variance limits. */
    for (i = 0; i < 700; i++) {
        double v = 50.0 + (i % 2 == 0 ? 0.1 : -0.1) * ch.calib_std;
        flag = diag_process(&ch, v);
    }
    assert(flag == DIAG_FLAG_GOOD);
    PASS("CUSUM detector: signal recovers -> Good");
}

static void test_ewma_detector(void) {
    DiagChannel ch;
    int flag, i;
    diag_init(&ch);
    calibrate(&ch, 50.0);

    /* Fast drift (0.5 * std per step): EWMA tracks quickly; ref_mean adapts slowly.
       After ~30 steps the gap |ewma - ref_mean| exceeds K_EWMA * calib_std. */
    flag = DIAG_FLAG_GOOD;
    for (i = 0; i < 50; i++) {
        flag = diag_process(&ch, 50.0 + (double)i * 0.5 * ch.calib_std);
    }
    assert(flag == DIAG_FLAG_POTENTIAL || flag == DIAG_FLAG_BAD);
    PASS("EWMA detector: fast drift -> Potential or Bad");
}

static void test_flag_priority(void) {
    DiagChannel ch;
    int flag, i;
    diag_init(&ch);
    calibrate(&ch, 50.0);

    /* Prime CUSUM with a large shift (20x std) so it's in Potential state */
    for (i = 0; i < 5; i++) {
        diag_process(&ch, 50.0 + 20.0 * ch.calib_std);
    }
    /* Now add a massive spike on top: rate detector fires -> Bad overrides Potential */
    flag = diag_process(&ch, 50.0 + 20.0 * ch.calib_std + 100.0 * ch.calib_std);
    assert(flag == DIAG_FLAG_BAD);
    PASS("flag priority: Bad overrides Potential");
}

int main(void) {
    test_init();
    test_calibration();
    test_calibration_outlier_rejection();
    test_rate_detector();
    test_variance_detector();
    test_cusum_detector();
    test_ewma_detector();
    test_flag_priority();
    printf("All tests passed.\n");
    return 0;
}
